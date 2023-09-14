<template>
  <div>
<!--    <div id="nav">-->
<!--      <router-link v-if="authenticated" to="/login" v-on:click.native="logout()" replace>Logout</router-link>-->
<!--    </div>-->
    <router-view @authenticated="setAuthenticated"/>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      authenticated: true,
    }
  },
  mounted() {
    if (!this.authenticated) {
      this.$router.replace({name: "login"});
    }
  },
  methods: {
    setAuthenticated(status) {
      this.authenticated = status;
      console.log('setAuthenticated: ', status);
      if (this.authenticated == true) {
        this.$router.replace({name: "dashboard"});
      }
    },
    logout() {
      this.authenticated = true;
    }
  }
}
</script>