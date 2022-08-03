<template>
	<div id="wrapper" class="device-main">
		<el-card class="box-card">
			<div slot="header" class="clearfix">
				<span>{{devicenName}}</span>
				<el-button style="float: right; padding: 3px 0" type="text">操作按钮</el-button>
			</div>
			<div v-for="o in 4" :key="o" class="text item">
				{{'列表内容 ' + o }}
			</div>
		</el-card>
	</div>
</template>

<script>
	import {
		ipcRenderer
	} from "electron"
	var onlineLoading = null

	ipcRenderer.on('mqtt-service', (event, arg) => {
		if (arg === 'onlineSuccess') {
			onlineLoading.close()
			return
		}
	})

	export default {
		data() {
			return {
				devicenName:"加载中"
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
			this.onSubmit()
			this.devicenName = localStorage.getItem("name")
		},

		methods: {
			async onSubmit() {
				await ipcRenderer.invoke("mq-online", "login")
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
	.onlineLoading .el-loading-spinner .el-loading-text {
		color: white;
		letter-spacing: 1px;
	}

	.onlineLoading .el-loading-spinner i {
		color: white;
		font-size: 30px;
		margin-bottom: 10px;
	}

	.device-main {
		margin-top: 40px;
		padding: 12px;
	}
</style>
