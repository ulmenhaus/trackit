import rethinkdb as r

# HACK should be a part of api
r.connect("172.16.131.129", 28015).repl()
r.db_create("trackit").run()
r.db("trackit").table_create("schemata", primary_key="name").run()
