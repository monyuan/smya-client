<template>
	<scroll-bar>
		<el-menu mode="horizontal" :show-timeout="200" :default-active="$route.path" :collapse="false">
			<Logo :collapse="isCollapse" />
			<sidebar-item v-for="route in permission_routes" :key="route.name" :item="route" :base-path="route.path"
				:collapse="isCollapse"></sidebar-item>
		</el-menu>
	</scroll-bar>
</template>

<script>
	import {
		mapGetters
	} from "vuex";
	import SidebarItem from "./SidebarItem";
	import ScrollBar from "@/components/ScrollBar";
	import Logo from "./logo";

	export default {
		components: {
			SidebarItem,
			ScrollBar,
			Logo
		},
		computed: {
			...mapGetters(["sidebar", "permission_routes"]),
			isCollapse() {
				console.log(this.$store.getters);
				return !this.sidebar.opened;
			},
		},
		mounted() {
			this.$nextTick(() => {
				if (!sessionStorage.getItem('leftBar')) {
					this.$store.commit("TOGGLE_SIDEBAR")
					sessionStorage.setItem('leftBar', 1)
				}
			})
		}
	};
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
	.title {
		text-align: center;
		line-height: 64px;
		height: 64px;
		font-size: 14px;
		font-weight: bold;
		color: #333333;
		background-color: #ffffff;
		padding: 0 20px;

		.logo-set {
			width: 21px;
			height: 21px;
		}
	}

	.minititle {
		padding: 0 10px;
		transition: padding 0.28s;
		overflow: hidden;
		width: 180px;
	}
</style>
