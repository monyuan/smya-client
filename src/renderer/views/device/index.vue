<template>
	<div id="wrapper" class="device-main">
		<div class="nav" style="-webkit-app-region: drag"></div>
		<el-card class="box-card" shadow="never">
			<div slot="header" class="clearfix">
				<span style="app-region: drag;">{{ devicenName }}</span>
				<el-button style="float: right; padding: 3px 0" type="text" @click="logout">切换设备</el-button>
			</div>
			<div class="text item device-content">
				<img src="https://p1.meituan.net/dpplatform/e4761a9cb52bc29d62186570e471a9482613985.gif"
					style="width: 160px;">
			</div>
		</el-card>
		<div class="log">
			<el-input type="textarea" :rows="9" placeholder="当前日志" :value="textarea" readonly id="log">
			</el-input>
		</div>
		<div class="disbale"></div>
	</div>
</template>

<script>
import {
	ipcRenderer
} from "electron"
var onlineLoading = null
var textarea = "服务端日志(只展示最近一条)：\n\n"

ipcRenderer.on('mqtt-service', (event, arg) => {
	if (arg === 'onlineSuccess') {
		onlineLoading.close()
		arg = "已连接到ORZLAB服务端"
	}
	document.getElementById('log').value = "服务端日志(只展示最近一条): \n\n" + arg;
})

export default {
	data() {
		return {
			devicenName: "加载中",
			textarea: textarea
		}
	},
	mounted() {
		onlineLoading = this.$loading({
			lock: true,
			text: '与ORZ实验室建立连接中...',
			spinner: 'el-icon-loading',
			background: 'black',
			customClass: 'onlineLoading'
		});
		this.online()
		this.devicenName = localStorage.getItem("name")
	},

	methods: {
		async online() {
			let data = {
				username: localStorage.getItem("sn"),
				password: localStorage.getItem("token"),
				host: "mqtt://emqx.orzlab.com:9004"
			}
			await ipcRenderer.invoke("mq-online", JSON.stringify(data))
		},
		async offline() {
			await ipcRenderer.invoke("mq-offline", "offline")
		},
		async logout() {
			let result = await this.offline()
			console.log(result)
			localStorage.removeItem("token")
			localStorage.removeItem("name")
			localStorage.removeItem("sn")
			this.$router.push({ path: '/login' }).catch(() => { })
		},
		onCancel() {
			this.$message({
				message: "cancel!",
				type: "warning"
			});
		}
	}
};
</script>

<style>
.device-content {
	text-align: center;
}

.disbale {
	position: absolute;
	z-index: 888;
	right: 0;
	width: 30px;
	height: 30px;
	bottom: -5px;
}

.log .el-textarea__inner:focus {
	border-color: #fff !important;
}

.log .el-textarea__inner {
	border-color: #fff !important;
}

.log .el-textarea__inner {
	font-size: 12px;
	color: #67C23A;
	background: #F2F6FC;
	width: 352px;
	margin-left: -1px;
	height: 183px;
}

.nav {
	width: 100%;
	height: 22px;
	position: absolute;
	top: 0;
}

.onlineLoading .el-loading-spinner .el-loading-text {
	color: white;
	letter-spacing: 1px;
}

.onlineLoading .el-loading-spinner i {
	color: white;
	font-size: 30px;
	margin-bottom: 10px;
}
</style>
