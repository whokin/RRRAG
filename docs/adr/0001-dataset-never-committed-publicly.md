# Scraped dataset is never committed to the public repo

The corpus is scraped from rationalreminder.ca, whose transcripts are Rational
Reminder's copyrighted content (tied to a registered investment firm), and
whose robots.txt signals clear discomfort with AI harvesting even though it
doesn't technically disallow episode pages. We publish our code and roadmap on
GitHub but keep all scraped data gitignored; its canonical home is a private
Cloudflare R2 bucket, and the product links back to source episodes for
attribution. Alternatives were a fully private project (loses the
learning-in-public value) or asking permission first (unnecessary if we don't
redistribute their content).
