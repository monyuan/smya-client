<template>
	<div id="app">
		<c-header></c-header>
		<transition name="fade" mode="out-in">
			<router-view></router-view>
		</transition>
	</div>
</template>

<script>
	import CHeader from "./components/title";

	export default {
		components: {
			CHeader
		},
		mounted() {
			let t1 = window.location.href.split("token=")[1]
			if (t1 !== undefined) {
				let t2 = t1.split("?state")[0]
				this.$local.set("token", t2)
			}
		}
	};
</script>

<style>
	/* CSS */
</style>
