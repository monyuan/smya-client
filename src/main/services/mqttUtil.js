import mqtt from "mqtt";
import {
	BrowserWindow,
	Notification
} from 'electron'
import cmdShell from "node-cmd"

var id = 2
class MqttUtil {
	onilne(event, options, topic, host) {
		id = event.sender.id
		const client = mqtt.connect(host, options);

		client.on("reconnect", () => {
			BrowserWindow.fromId(id).send('mqtt-service', '连接服务器中，请稍后...')
		});

		client.on("connect", () => {
			BrowserWindow.fromId(id).send('mqtt-service', 'onlineSuccess')
			client.subscribe("smy-topic/" + topic, {
				qos: 0,
			});
		});

		client.on("message", (topic, message, packet) => {
			console.log("message")
			this.do(message)
			BrowserWindow.fromId(id).send('mqtt-service', 'server：' + message.toString())
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
		BrowserWindow.fromId(id).send('mqtt-service', '是否支持消息通知：' + Notification.isSupported())
		new Notification({
			title: title,
			body: body
		}).show()
	}
}

export default MqttUtil
