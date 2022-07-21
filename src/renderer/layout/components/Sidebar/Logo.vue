<template>
  <div class="sidebar-logo-container" :class="{'collapse':collapse}">
    <transition name="sidebarLogoFade">
      <router-link v-if="collapse" key="collapse" class="sidebar-logo-link" to="/">
        <img class="left-logo" src="https://m.360buyimg.com/babel/jfs/t1/184715/5/27015/6533/62d3d3f2Ed161a178/47317abce57cb18b.png"/>
        <!-- <div class="sidebar-title">{{ title }}</div> -->
      </router-link>
      <router-link v-else key="expand" class="sidebar-logo-link" to="/">
        <img  class="left-logo" src="https://m.360buyimg.com/babel/jfs/t1/184715/5/27015/6533/62d3d3f2Ed161a178/47317abce57cb18b.png"/>
        <!-- <div class="sidebar-title">{{ title }}</div> -->
      </router-link>
    </transition>
  </div>
</template>

<script>
export default {
  name: "SidebarLogo",
  props: {
    collapse: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      title: "神秘鸭",
    };
  }
};
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
.sidebarLogoFade-enter-active {
  transition: opacity .28s;
}

.left-logo{
	width: 70px;
	margin-top: 14px;
}

.sidebarLogoFade-enter,
.sidebarLogoFade-leave-to {
  opacity: 0;
}

.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 100px;
  line-height: 100px;
  text-align: center;
  overflow: hidden;
  background-color: #ffffff;
  box-shadow: none!important;

  & > .sidebar-logo-link {
    height: 100%;
    width: 100%;

    & > .sidebar-logo {
      width: 32px;
      height: 32px;
      vertical-align: middle;
      margin-right: 12px;
    }

    & > .sidebar-title {
      display: inline-block;
      margin: 0;
      color: #333;
      font-weight: 600;
      line-height: 50px;
      font-size: 14px;
      font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
      vertical-align: middle;
    }
  }
}
.collapse {
  .sidebar-logo {
    margin-right: 0px !important;
    margin-left: 0px !important;
  }
}
</style>