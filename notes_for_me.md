scan groceries receipts -> extract data (what, how many, how much etc) -> store in data base -> create FAST Api endpoints -> give them to agent to answer questions and do analysis

## Part 1
Create database - read pdfs - ocr and layout detection - convert to standard pandas - store in database

For POC, Google Drive storage and PostgreSQL for database
LLM to convert layout info into structured, pre-defined pandas df

## Part 2
wrap db queries into apis

## Part 3
Create agent and provide APIs as tools