# FUNCTION TO WRITE HTML 
from pathlib import Path
import os
import datetime
import config
from Update_flags import matched_filters

 # TODAY'S DATE
date_str = datetime.datetime.now().strftime("%Y-%m-%d")

def write_html_digest(jobs, fields):
    ats = ["greenhouse", "lever", "ashby", "workday"]

    for platform in ats:
        title = f"{platform} Job URLs — {date_str}"
        ats_jobs = [job for job in jobs if job.get("platform", "").lower() == platform]  

        if not ats_jobs:
           continue

        # Append platform to filename
        #path = Path(filename)
        path = r"D:\Agent\daily-digest"
        ats_filename = os.path.join(config.DIGEST_DIR, f"{date_str}_{platform}_URLs.html")
        # ats_filename = path.with_name(f"{path.stem}_{platform}{path.suffix}")  
        # top10_URLs_path = os.path.join(config.DIGEST_DIR, f"{date_str}_Top10.html")
        
        # WRITE HTML
        with open(ats_filename, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
                <html>
                <head>
                <title>{title}</title>
                <style>
                body {{ font-family: Arial, sans-serif; }}
                .job {{ margin-bottom: 20px; }}

                hr {{
                    border: 0;
                    border-top: 2px solid #888;
                    margin: 25px 0;
                    }}
                </style>
                </head>
                <body>

                <h1>{title}</h1>
                """)

            for i, job in enumerate(ats_jobs): 
                f.write(f"""
                    <div class="job">
                    <h2>{i+1}. {job.get('company')} — {job.get('title')}</h2>
                    """)

                for label, key in fields:
                    # f.write(f"<p><b>{label}:</b> {job.get(key, '')}</p>\n")

                    value = job.get(key, "")

                    if key == "url" and value:
                        f.write(f'<p><b>{label}:</b> <a href="{value}" target="_blank">{value}</a></p>\n')
                    elif key == "score":
                        tags = matched_filters(job)
                        suffix = f" ({tags})" if tags else ""
                        f.write(f"<p><b>{label}:</b> {value}{suffix}</p>\n")     
                    else:
                        f.write(f"<p><b>{label}:</b> {value}</p>\n")

                # f.write("</div>\n")
                f.write("</div>\n<hr>\n")

            f.write("""
                </body>
                </html>
                """)

        print(f"\nWrote {ats_filename}")