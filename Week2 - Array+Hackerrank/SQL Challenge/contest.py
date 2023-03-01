import datetime

def get_submission_data():
    submission_dates = []
    submission_counts = []
    hacker_ids = []
    hacker_names = []
    current_date = None

    # Subquery to get earliest submission date for each hacker with most submissions on that date
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT n.submission_date, n.hacker_id, COUNT(n.submission_id)
            FROM Submissions n
            GROUP BY submission_date, hacker_id
            HAVING COUNT(submission_id)>= ALL(
                  SELECT COUNT(m.submission_id)
                  FROM Submissions m
                  GROUP BY m.submission_date, m.hacker_id
                  HAVING m.submission_date=n.submission_date
              )
            ORDER BY submission_date ASC
        """)

        for row in cursor.fetchall():
            submission_date = row[0]
            hacker_id = row[1]
            count = row[2]

            if submission_date != current_date:
                # New submission date found; append data to lists
                submission_dates.append(submission_date)
                submission_counts.append(count)
                hacker_ids.append(hacker_id)
                current_date = submission_date
            else:
                # Same submission date; replace last count and hacker ID in lists
                submission_counts[-1] = count
                hacker_ids[-1] = hacker_id

    # Subquery to get number of distinct hackers who submitted on 2016-03-01 or satisfy other conditions
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT aa.submission_date, COUNT(DISTINCT aa.hacker_id) AS contSub
            FROM Submissions AS aa
            WHERE aa.submission_date=%s 
            OR submission_date<ALL(
                SELECT bb.submission_date
                FROM (
                    SELECT tdy.hacker_id, tdy.submission_date, ytd.submission_date AS SubmittedYtd
                    FROM Submissions tdy LEFT JOIN Submissions ytd
                    ON DATE_ADD(tdy.submission_date, INTERVAL -1 DAY)= ytd.submission_date 
                    AND ytd.hacker_id=tdy.hacker_id    
                ) AS bb
                WHERE aa.hacker_id=bb.hacker_id AND bb.submission_date<> %s AND bb.SubmittedYtd IS NULL
            )
            GROUP BY aa.submission_date
            ORDER BY aa.submission_date ASC
        """, ('2016-03-01', datetime.date(2016, 3, 1)))

        contSub = {row[0]: row[1] for row in cursor.fetchall()}

    # Join data from both subqueries and retrieve hacker names
    result = []
    for submission_date, count, hacker_id in zip(submission_dates, submission_counts, hacker_ids):
        result.append((submission_date, contSub.get(submission_date, 0), hacker_id))

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT hacker_id, name
            FROM Hackers
        """)

        nameDict = {row[0]: row[1] for row in cursor.fetchall()}

    result = [(date, count, hacker_id, nameDict.get(hacker_id)) for date, count, hacker_id in result]

    # Sort results by submission date
    result.sort(key=lambda x: x[0])

    return result
