# trackit: JSON data collection and schema validation on the web

## What it is

Trackit is a service you run that lets users track data they collect over time. It has a simple URL schema for posting and collecting data points and even has a slackbot that can prompt users for their data and make the data available on the web.


## How it works

Once running trackit operates with a simple URL schema. URLs are of the form

```
https://trackit/<namespace>/<schema_name>/<data_key>
```

denotes a single datum for a given schema within a "namespace" (space of schemata owned by a given user). To get started you can create an example schema with

```bash
$ cat > schema.json
{
    "slept_in": {
        "type": "bool",
        "prompt": "Did you sleep in?"
    },
    "breakfast": {
        "type": "string",
        "prompt": "What did you have for breakfast?"
    }
}
```

and post to trackit with


```bash
curl -H "Content-type: application/json" -X PUT https://trackit/schemata/rabrams/daily/ -d @schema.json
```

Now you can create a datum for that schema

```bash
$ cat > datum.json
{
    "slept_in": true,
    "breakfast": "eggs"
}
```

and add it

```bash
curl -H "Content-type: application/json" -X PUT https://trackit/data/rabrams/daily/latest/ -d @datum.json
```

and get all data with

```bash
curl https://trackit/data/rabrams/daily/
```

additionally you can run a bot in slack that will automatically look for schemata named `daily` and use those to prompt users for their daily bits of biodata.

## How to develop/operate it

To get started you should get [Docker](https://docs.docker.com/engine/installation/) and then run


```bash
docker-compose up
```

which will build the different microservice images and run then on your engine. By default you'll be missing the environment variables necessary to make the slackbot work but the service will run anyway. To run the service fully set the following environment variables


* *TRACKIT_SLACK_TOKEN*: your slack API token
* *TRACKIT_BOTMASTER*: the name of the slack botmaster (who will manage the slackbot)
* *TRACKIT_USERS*: a comma-separated list of users slackbot should prompt for information
* *TRACKIT_CHANNEL*: the channel in which slackbot should operate
* *TRACKIT_PUBLIC_ENDPOINT*: the internet reachable trackit endpoint (only used to display URLs)

once running, slackbot will prompt the bot master. a response of `@trackbot trigger` will cause the slackbot to go and collect data.

## Testing
Please ensure that changes you make are tested and pass our linting and formatting standards. To verify all tests you can bring up the service and then run

```bash
docker-compose run --rm tester all
```
