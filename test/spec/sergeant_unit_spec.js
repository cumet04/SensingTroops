var frisby = require('frisby');

var addr = process.env.addr
var port = process.env.port
if(addr == undefined) addr = 'localhost'
if(port == undefined) port = '51000'
var ep = 'http://' + addr + ':' + port;

frisby.create('GET info')
    .get(ep + '/info')
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

frisby.create('POST join')
    .post(ep + '/pvt/join', {
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
        frisby.create('GET pvt/list')
            .get(ep + '/pvt/list')
            .addHeader('Content-Type', 'application/json')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON('pvt_list.?', new String(test_id))
            .toss()

        frisby.create('POST work')
            .post(ep + '/pvt/' + test_id + '/work', {
                    sensor: "random",
                    value: 0.11
                }, {json: true})
            .addHeader('Content-Type', 'application/json')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON({result: "success"})
            .toss()

        frisby.create('GET pvt/{id}/info')
            .get(ep + '/pvt/' + test_id + '/info')
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
    .put(ep + '/sgt/job/report', {
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
            .get(ep + '/sgt/job/report')
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
    .post(ep + '/pvt/invalid-id/work', {
            sensor: "random",
            value: 0.11
        }, {json: true})
    .addHeader('Content-Type', 'application/json')
    .expectStatus(404)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({msg: 'the pvt is not my soldier'})
    .toss()

frisby.create('GET pvt/info (invalid id)')
    .get(ep + '/pvt/invalid-id/info')
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
    .put(ep + '/sgt/job/command', {
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
            .get(ep + '/sgt/job/command')
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
    .put(ep + '/sgt/job/command', {
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
    .put(ep + '/sgt/job/report', {
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

