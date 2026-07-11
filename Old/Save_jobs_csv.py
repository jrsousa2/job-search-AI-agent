# ADDED THIS FUNCTION TO SAVE OUTPUT AS CSV
def save_jobs_csv(jobs: list[dict]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "company",
        "title",
        "location",
        "is_remote",
        "platform",
        "slug",
        "url",
        "job_id",
        "description",]

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(jobs)

    print(f"\nSaved {len(jobs)} jobs to {OUTPUT_CSV}")