var frisby = require('frisby');

var ep = process.env.ep
var id = process.env.id
if(ep == undefined) ep = 'http://localhost:52000/commander'
if(id == undefined) id = ''

frisby.create('GET info')
    .get(ep)
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        info: {
            name: 'com-http',
            endpoint: ep,
            campaigns: [],
            id: id,
            subordinates: []
        }
    })
    .toss();

/*
frisby.create('GET info')
    .get(ep)
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        info: {
            name: 'sgt-http',
            port: Number(port)
        }
    })
    .expectJSONTypes('info.addr', String)
    .toss();

var test_id = "test_id";

frisby.create('POST soldiers')
    .post(ep + '/soldiers', {
            id: test_id,
            name: "test-name",
            addr: addr,
            port: Number(port),
            sensors: ["random", "zero", "test-sensor"]
        }, {json: true})
    .addHeader('Content-Type', 'application/json')
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        accepted: {
            id: test_id,
            name: "test-name",
            addr: addr,
            port: Number(port),
            sensors: ["random", "zero", "test-sensor"]
        }
    })
    .after(function(err, res, body)
    {
        frisby.create('GET soldiers')
            .get(ep + '/soldiers')
            .addHeader('Content-Type', 'application/json')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON('pvt_list.?', new String(test_id))
            .toss()

        frisby.create('POST work')
            .post(ep + '/soldiers/' + test_id + '/work', {
                    sensor: "random",
                    value: 0.11
                }, {json: true})
            .addHeader('Content-Type', 'application/json')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON({result: "success"})
            .toss()

        frisby.create("GET pvt's info")
            .get(ep + '/soldiers/' + test_id)
            .addHeader('Content-Type', 'application/json')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON({
                id: test_id,
                name: "test-name",
                addr: addr,
                port: Number(port),
                sensors: ["random", "zero", "test-sensor"]
            })
            .toss()

    })
    .toss();

var report_job = {
        interval: 5,
        encoding: "flat",
        filter: [{include: "random"}]
    }
frisby.create('PUT job/report')
    .put(ep + '/job/report', {
        report_job: report_job
    }, {json: true})
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        report_job: report_job
    })
    .after(function(err, res, body)
    {
        frisby.create('GET job/report')
            .get(ep + '/job/report')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON({
                result: 'success',
                report_job: report_job
            })
            .toss();
    })
    .toss();


// invalid id test ----------------------------------------

frisby.create('POST work (invalid id)')
    .post(ep + '/soldiers/invalid-id/work', {
            sensor: "random",
            value: 0.11
        }, {json: true})
    .addHeader('Content-Type', 'application/json')
    .expectStatus(404)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({msg: 'the pvt is not my soldier'})
    .toss()

frisby.create("GET pvt's info (invalid id)")
    .get(ep + '/soldiers/invalid-id')
    .addHeader('Content-Type', 'application/json')
    .expectStatus(404)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({msg: 'the pvt is not my soldier'})
    .toss()

var command_jobs = [
        {
            target: "all",
            order: {
                sensor: "random",
                interval: 2
            }
        }
    ]
frisby.create('PUT job/command')
    .put(ep + '/job/command', {
        command_jobs: command_jobs
    }, {json: true})
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        command_jobs: command_jobs
    })
    .after(function(err, res, body)
    {
        frisby.create('GET job/command')
            .get(ep + '/job/command')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON({
                result: 'success',
                command_jobs: command_jobs
            })
            .toss();
    })
    .toss();


// content-type test ----------------------------------------

frisby.create('PUT job/command (invalid content-type)')
    .put(ep + '/job/command', {
            sensor: "random",
            value: 0.11
        }, {json: true})
    .addHeader('Content-Type', 'application/xml') // NOT json
    .expectStatus(406)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'failed',
        msg: 'application/json required'
    })
    .toss()

frisby.create('PUT job/report (invalid content-type)')
    .put(ep + '/job/report', {
            sensor: "random",
            value: 0.11
        }, {json: true})
    .addHeader('Content-Type', 'application/xml') // NOT json
    .expectStatus(406)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'failed',
        msg: 'application/json required'
    })
    .toss()

*/
