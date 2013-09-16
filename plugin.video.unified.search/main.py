from searches_db import Search

db = Search()
db.save("test1")


# db.drop()
searches = db.all()
print searches

