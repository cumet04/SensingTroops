var frisby = require('frisby');

var addr = process.env.addr
var port = process.env.port
if(addr == undefined) addr = 'localhost'
if(port == undefined) port = '50000'
var ep = 'http://' + addr + ':' + port + '/private'

frisby.create('GET info')
    .get(ep)
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        info: {
            name: 'pvt-http',
            port: Number(port),
        }
    })
    .expectJSONTypes('info.addr', String)
    .expectJSON('info.sensors.?', new String("random"))
    .expectJSON('info.sensors.?', new String("zero"))
    .toss();

frisby.create('PUT order (single object)')
    .put(ep + '/order', {
            orders: {sensor: "random", interval: 2}
        }, {json: true})
    .addHeader('Content-Type', 'application/json')
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        orders: [{sensor: "random", interval: 2}]
    })
    .toss();

frisby.create('PUT order (single list)')
    .put(ep + '/order', {
            orders: [{sensor: "random", interval: 2}]
        }, {json: true})
    .addHeader('Content-Type', 'application/json')
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        orders: [{sensor: "random", interval: 2}]
    })
    .toss();

frisby.create("PUT order (multiple object's list)")
    .put(ep + '/order', {
            orders: [
                {sensor: "random", interval: 2},
                {sensor: "zero", interval: 5}
            ]
        }, {json: true})
    .addHeader('Content-Type', 'application/json')
    .expectStatus(200)
    .expectHeaderContains('Content-Type', 'application/json')
    .expectJSON({
        result: 'success',
        orders: [
            {sensor: "random", interval: 2},
            {sensor: "zero", interval: 5}
        ]
    })
    .after(function(err, res, body)
    {
        frisby.create('GET order')
            .get(ep + '/order')
            .addHeader('Content-Type', 'application/json')
            .expectStatus(200)
            .expectHeaderContains('Content-Type', 'application/json')
            .expectJSON({
                result: 'success',
                orders: [
                    {sensor: "random", interval: 2},
                    {sensor: "zero", interval: 5}
                ]
            })
            .toss();
    })
    .toss();


frisby.create('PUT order (request header failure)')
    .put(ep + '/order', {
            orders: {sensor: "random", interval: 2}
        }, {json: true})
    .addHeader('Content-Type', 'application/xml') // not json
    .expectStatus(406)
    .expectJSON({
        result: 'failed',
        msg: 'application/json required'
    })
    .toss();

frisby.create('PUT order (request method failure)')
    .post(ep + '/order', { // not put
            orders: {sensor: "random", interval: 2}
        }, {json: true})
    .addHeader('Content-Type', 'application/json')
    .expectStatus(405)
    .toss();

var invalid_json = '"orders": {"sensor": "random", "interval": 2}}'
frisby.create('PUT order (invalid json data failure)')
    .put(ep + '/order', new Buffer(invalid_json))
    .addHeader('Content-Type', 'application/json') // not json
    .expectStatus(400)
    .expectJSON({
        result: 'failed',
        msg: "param couldn't decode to json"
    })
    .toss();

