import mqtt from "mqtt";
import {
	BrowserWindow,
	Notification
} from 'electron'
import cmdShell from "node-cmd"

var id = 2
var client = null;
class MqttUtil {

	offline() {
		client.end()
	}
	onilne(event) {
		const clientId = "mqttjs_" + Math.random().toString(16).substr(2, 8);
		const host = "mqtt://emqx.orzlab.com:9004";
		const options = {
			keepalive: 30,
			clientId: clientId,
			protocolId: "MQTT",
			protocolVersion: 4,
			clean: true,
			username: "12345678",
			password: "123456",
			reconnectPeriod: 1000,
			connectTimeout: 30 * 1000,
			will: {
				topic: "WillMsg",
				payload: "Connection Closed abnormally..!",
				qos: 0,
				retain: false,
			},
			rejectUnauthorized: false,
		};
		id = event.sender.id
		client = mqtt.connect(host, options);

		client.on("reconnect", () => {
			BrowserWindow.fromId(id).send('mqtt-service', '连接服务器中，请稍后...')
		});

		client.on("connect", () => {
			BrowserWindow.fromId(id).send('mqtt-service', 'onlineSuccess')
			client.subscribe("testtopic/electron", {
				qos: 0,
			});
		});

		client.on('offline', function() {
			console.log('offline');
		});

		client.on("message", (topic, message, packet) => {
			BrowserWindow.fromId(id).send('mqtt-service', message.toString())
			this.do(message)
		});

	}

	sendMsg(client) {
		client.publish("testtopic/electron", "Electron connection demo...!", {
			qos: 0,
			retain: false,
		});
	}

	do(msg) {
		let msgJson = JSON.parse(msg)
		switch (msgJson.type) {
			case "shell":
				this.shell(msgJson.body)
				break
			case "message":
				console.log("do")
				this.msg(msgJson.title, msgJson.body)
				break
		}
	}

	shell(text) {
		cmdShell.run(text)
	}

	msg(title, body) {
		// BrowserWindow.fromId(id).send('mqtt-service', '是否支持消息通知：' + Notification.isSupported())
		new Notification({
			title: title,
			body: body
		}).show()
	}
}

export default MqttUtil
