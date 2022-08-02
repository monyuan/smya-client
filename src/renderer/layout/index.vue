<template>
  <div class="app-wrapper" :class="IsUseSysTitle ? 'UseSysTitle' : 'NoUseSysTitle'">
      <div class="main-container">
        <app-main></app-main>
      </div>
    </div>
</template>

<script>
import { AppMain } from "./components";
import ResizeMixin from "./mixin/ResizeHandler";

export default {
  name: "layout",
  components: {
    AppMain
  },
  mixins: [ResizeMixin],
  data: () => ({
    IsUseSysTitle: require("./../../../config").IsUseSysTitle
  }),
  computed: {
    sidebar() {
      return this.$store.state.app.sidebar;
    },
    device() {
      return this.$store.state.app.device;
    },
    classObj() {
      return {
        hideSidebar: !this.sidebar.opened,
        openSidebar: this.sidebar.opened
      };
    }
  }
};
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import "@/styles/mixin.scss";

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100%;
  width: 100%;

  .container-set {
    position: relative;
    padding-top: 62px;
  }
}

.UseSysTitle {
  top: 0px;
}

.NoUseSysTitle {
  top: 38px
}
</style>
