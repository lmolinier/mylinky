# mylinky
Linky utilites to grab your power consumption from ENEDIS website


### InfluxDB
To configure a fresh and simple InfluxDB installation, follow those steps:

#### Create database

Create database
```
> CREATE DATABASE linky
> CREATE USER "linky" WITH PASSWORD [REDACTED]
> GRANT ALL ON "linky" TO "linky"
```

#### Alter default retention and tune it as you want

Example : 5 years (1825d)
```
> ALTER RETENTION POLICY "autogen" ON "linky" DURATION 1825d SHARD DURATION 7d DEFAULT
```
