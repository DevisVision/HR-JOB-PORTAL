"""
Test all job aggregators.
"""

from services.aggregators.adzuna import fetch_adzuna_jobs
from services.aggregators.arbeitnow import fetch_arbeitnow_jobs
from services.aggregators.remotive import fetch_remotive_jobs
from services.aggregators.remoteok import fetch_remoteok_jobs
from services.aggregators.themuse import fetch_themuse_jobs

# Uncomment after configuring USAJobs credentials
# from services.aggregators.usajobs import fetch_usajobs


def test_source(name, function):

    print("\n" + "=" * 70)
    print(name.upper())
    print("=" * 70)

    try:

        jobs = function()

        print(f"Retrieved {len(jobs)} jobs")

        if jobs:

            print("\nSample Job\n")

            print(jobs[0])

        else:

            print("No jobs returned.")

    except Exception as e:

        print(e)


def main():

    test_source(
        "Adzuna",
        fetch_adzuna_jobs
    )

    test_source(
        "Arbeitnow",
        fetch_arbeitnow_jobs
    )

    test_source(
        "Remotive",
        fetch_remotive_jobs
    )

    test_source(
        "RemoteOK",
        fetch_remoteok_jobs
    )

    test_source(
        "The Muse",
        fetch_themuse_jobs
    )

    # test_source(
    #     "USAJobs",
    #     fetch_usajobs
    # )


if __name__ == "__main__":

    main()