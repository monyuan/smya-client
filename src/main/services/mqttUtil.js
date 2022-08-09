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
		console.log("end")
		client.end()
	}

	onilne(event, options, topic, host) {

		id = event.sender.id
		client = mqtt.connect(host, options);

		client.on("reconnect", () => {
			BrowserWindow.fromId(id).send('mqtt-service', '连接服务器中，请稍后...')
		});

		client.on("connect", () => {
			BrowserWindow.fromId(id).send('mqtt-service', 'onlineSuccess')
			client.subscribe("smy-topic/" + topic, {
				qos: 0,
			});
		});

		client.on("error", (err) => {
			console.log("Connection error: ", err);
			client.end();
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

		if(!title){
			title = "来自神秘鸭服务端消息"
		}
		new Notification({
			title: title,
			body: body
		}).show()
	}
}

export default MqttUtil
