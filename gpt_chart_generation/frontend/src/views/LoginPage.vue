<template>
  <v-app>
    <v-container bg fill-height grid-list-md text-xs-center>
      <v-layout row wrap align-center>
        <v-card class="mx-auto px-6 py-8" max-width="400">
          <v-card-title>RISE Intelligent Planning Tool</v-card-title>
            <v-text-field
                v-model="input.username"
                class="mb-2"
                clearable
            ></v-text-field>

            <v-text-field
                v-model="input.password"
                type="password"
                clearable
                placeholder="Enter your password"
            ></v-text-field>
            <br>
            <v-btn
                block
                color="success"
                size="large"
                type="submit"
                variant="elevated"
                v-on:click="login()"
            >
              Sign In
            </v-btn>
        </v-card>
      </v-layout>
    </v-container>
  </v-app>
</template>

<script>
// import axios from "axios";
import { performLogin } from "@/api";

export default {
  name: 'LoginPage',
  data() {
    return {
      input: {
        username: "",
        password: ""
      },
    }
  },
  methods: {
    async login() {
      await performLogin(this.input.username, this.input.password)
          .then((authenticated) => {
            console.log('login: ', authenticated);
            this.$emit("authenticated", authenticated);
          });
    }
  }
}
</script>

<style scoped>
#login {
  width: 500px;
  border: 1px solid #CCCCCC;
  background-color: #FFFFFF;
  margin: auto;
  margin-top: 200px;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>