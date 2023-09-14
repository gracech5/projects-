<template>
  <v-app>
    <v-row class="text-center mb-n1 mt-10">
      <v-container fluid>
        <v-row align="center" class="ml-5 mr-5">
          <v-col class="mb-1" cols="12">
            <h1 class="headline font-weight-bold mb-10 mt-6" style="font-size: 30px !important; ">
              GPT Chart Generation Application
            </h1>
            <template>
              <v-row justify="center" align="center">

                <v-col cols="9" class="flex-grow-1">
                  <v-text-field type="text" v-model="searchText" height="100px"
                    :style="{ 'font-size': '25px', 'border-color': 'black' }" outlined
                    @keydown.enter.prevent="generate_process('/parse_input', '/chart')">
                    <template v-slot:label>
                      <label style="font-size: 18px; margin-left: 12px;color :black">Describe the Chart You Want</label>
                    </template>
                  </v-text-field>

                </v-col>
                <v-col cols="auto">
                  <v-btn color="#eceff1" @click="generate_process('/parse_input', '/chart')" class="mb-7 ml-3"
                    height="85px" width="130px" style="font-size: 18px;" x-large block>
                    Draw
                  </v-btn>
                </v-col>
                <v-col cols="auto">
                  <v-btn color="#eceff1" @click="clearinput()" class="mb-7 ml-3" height="85px" width="130px"
                    style="font-size: 18px;" x-large block>
                    Reset
                  </v-btn>
                </v-col>

                <template>
                  <div class="buttons" style="position: absolute; top: 10px; right: 10px">
                    <v-btn color="#eceff1" @click="toggleAlert" height="40px">
                      {{ showAlert ? "Close" : "Instruction" }}
                    </v-btn>
                  </div>
                </template>
              </v-row>

            </template>
            <v-row justify='center' v-if="showAlert">
              <div v-if="showAlert"
                style="background-color: #FFFFFF;position:relative; border: 1px solid #ccc; padding: 15px; margin-top: 10px;">

                <h2 text-align="center" style="font-size: 18px;line-height: 2;"> Get started from the examples below.</h2>

                <v-btn justify='center' class="button" v-for="(button, index) in buttons" :key="index"
                  :class="{ active: button.isActive }" @click="toggleButtonText(index)" color="#eceff1"
                  style="margin-left: 20px;margin-right: 20px;margin-top: 10px;margin-bottom: 10px;height:50px">
                  {{ button.text }}
                </v-btn>
                <h2 text-align="center" style="font-size: 18px;line-height: 2;"> Create your own query using the available
                  keywords below. </h2>
                <v-btn @click="showkeywords()" justify='center' color="#eceff1"
                  style="margin-left: 20px;margin-right: 20px;margin-top: 10px;margin-bottom: 10px;height:50px">
                  {{ keyword_display ? "Close" : "Available Keywords" }}
                </v-btn>
                <div v-if="keyword_display">
                  <h2 style="font-size: 18px;line-height: 2;text-align: left;">1. Chart Type: </h2>
                  <span style="font-size: 16px;line-height: 2;text-align: left;padding-left: 30px;display:block ">
                    scatterplot, treeplot, barplot </span>
                  <h2 style="font-size: 18px;line-height: 2;text-align: left;">2. Financial Indicator: </h2>
                  <span style="font-size: 16px;line-height: 2;text-align: left;padding-left: 30px;display:block"> ACV YoY
                    % , Win Rate , BUD Attain , # of Accounts , Avg Deal Size ,
                    # of AEs , ACV per AE , # of Accounts per AE , <br>COPA (Revenue) ,
                    REV YoY % , Market YoY % , Market Share %', MS Changes (pp.) ,
                    %Direct Rev Covered by CSPs ,<br> %Private Bookings Covered by CAAs ,
                    %Private Bookings Covered by PLs , Private Bookings Covered by CDMs </span>
                  <h2 style="font-size: 18px;line-height: 2;text-align: left;">3. Region: </h2>
                  <span style="font-size: 16px;line-height: 2;text-align: left;padding-left: 30px;display:block"> Region
                    L1 - BM , Region L2 - B , Region L3 , Region Country -M ,
                    2022 Sub-Solution Area - BM , 2022 Solution Area L3 , Channel ,<br>
                    Distribution Channel , Industry Sector - M , Industry Sector - M ,
                    ISS , IAC , S/4 Deployment , RISE Flag , <br>Material ID , 2023 Sub-Solution Area ,
                    2023 Solution Area L3 </span>
                </div>
                <div>
                  <v-btn color="#eceff1" class="close-button" icon @click="toggleAlert()"
                    style="position: absolute;top: 10px;right: 10px;">
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                </div>
              </div>
            </v-row>

          </v-col>
        </v-row>

      </v-container>
    </v-row>
    <v-row>
      <v-col>
        <div v-if="chart_type" style="display: flex; justify-content: center; align-items: center;">
          <h2 v-if="chart_type === 'treemap'" style="display: block;">{{ 'Chart Type: ' + this.chart_type +
            '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Path: ' + this.path
            + '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Value: ' + this.value +
            '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Filter: ' + this.filter
            + '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Color: ' + this.colour }}
          </h2>
          <h2 v-if="chart_type === 'scatter'" style="display: block;">{{ 'Chart Type: ' + this.chart_type +
            '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Path: ' + this.path
            + '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'X-axis: ' + this.value[0] +
            '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Y-axis: ' + this.value[1] }}</h2>
          <h2 v-if="chart_type === 'bar'" style="display: block;">{{ 'Chart Type: ' + this.chart_type +
            '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Path: ' + this.path
            + '&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;' + 'Value: ' + this.value }}</h2>
          <h2 v-show="this.msg_kw" style="display: block;">{{ 'Keyword Error Message: ' + this.msg_kw }}</h2>
          <h2 v-show="this.msg_chart" style="display: block;">{{ 'Chart Error Message: ' + this.msg_chart }}</h2>

        </div>
      </v-col>
    </v-row>
    <!--    <v-main>-->
    <template v-if="showaxis">
      <Plotly v-if="!errored" :data="data" :layout="layout" :display-mode-bar="false" style="height: 100%; width:100%"
        class="mt-n1"></Plotly>
      <v-main v-if="errored">
        <v-row align="center" class="ml-5 mr-5">
          <v-col v-for="n in 3" :key="n">
            <v-alert v-if="n == 2" type="error" class="mb-16">{{ errorMessage }}</v-alert>
          </v-col>
        </v-row>
      </v-main>
    </template>
  </v-app>
</template>

<script>
import { Plotly } from 'vue-plotly'
import { get_kw, get_c } from '@/api'

export default {
  name: 'DashboardPage',

  components: {
    Plotly,
  },

  data: () => ({
    data: null,
    layout: {},
    buttons: [
      { text: 'Scatterplot Example', isActive: false },
      { text: 'Treeplot Example', isActive: false },
      { text: 'Barplot Example', isActive: false }
    ],
    searchText: null,
    errored: null,
    errorMessage: null,
    showAlert: false,
    isInputConfirmed: false,
    jsonfile: null,
    chart_type: null,
    value: null,
    path: null,
    filter: null,
    colour: null,
    msg_kw: null,
    msg_chart: null,
    scatter_examplelist: [{ sentence: "scatterplot of winrate and acvbooking in country", ct: "scatter", rg: "Region Country", vl: ["Win Rate", 'ACV (Bookings)'] }],
    tree_examplelist: [{ sentence: "treeplot of acvbooking in regionl1 and region l2 and region l3", ct: "treemap", rg: ['Region L1', 'Region L2', 'Region L3'], vl: 'ACV (Bookings)' }],
    bar_examplelist: [{ sentence: "barplot of acvbooking in region l2", ct: "bar", rg: 'Region L2', vl: 'ACV (Bookings)' }],
    loading_label: false,
    keyword_display: false,
    wordList: ['scatterplot'],
    showaxis: false,

    // items: ['', 'Account Owner Name', 'Account Owner ID', 'Region L1','Region L2','Region L3','Region Country','IAC','ISS',
  }),

  mounted() {
  },

  methods: {
    async selectRandomText(examplelist) {
      this.clearinfo()
      const randomIndex = Math.floor(Math.random() * examplelist.length);
      this.searchText = examplelist[randomIndex]['sentence'];
      this.chart_type = examplelist[randomIndex]['ct'];
      this.path = examplelist[randomIndex]['rg'];
      this.value = examplelist[randomIndex]['vl'];
    },
    async toggleButtonText(index) {
      this.buttons.forEach((button, i) => {
        if (i === index) {
          button.text = 'Try Another One';
          button.isActive = true;
          this.selectRandomText(this.getExampleList(i))

        } else {
          button.text = this.getInitialButtonText(i);
          button.isActive = false;
        }
      })
    },
    getInitialButtonText(index) {
      // Define the initial text for each button based on the index
      // Modify this function to suit your naming requirements
      switch (index) {
        case 0:
          return 'Scatterplot Example';
        case 1:
          return 'Treemap Example';
        case 2:
          return 'Barplot Example';

        // Add more cases for additional buttons

      }
    },
    getExampleList(index) {
      // Define the initial text for each button based on the index
      // Modify this function to suit your naming requirements
      switch (index) {
        case 0:
          return this.scatter_examplelist;
        case 1:
          return this.tree_examplelist;
        case 2:
          return this.bar_examplelist;

        // Add more cases for additional buttons

      }
    },
    async clearinfo() {
      this.searchText = null;
      this.chart_type = null;
      this.path = null;
      this.value = null;
      this.filter = null;
      this.colour = null;
      this.msg_kw = null;
    },
    async clearinput() {
      this.clearinfo()
      this.buttons.forEach((button, i) => {
        button.text = this.getInitialButtonText(i);
        button.isActive = false;
      })
    },
    async toggleAlert() {
      this.showAlert = !this.showAlert;
    },
    async confirmInput() {
      this.isInputConfirmed = true;
    },
    async showkeywords() {
      this.keyword_display = !this.keyword_display;
    },


    async get_keyword(url) {
      console.log('Query: ', this.searchText);
      try {
        const user_input = this.searchText
        const responseData = await get_kw(url, user_input);
        this.chart_type = responseData['chart_type'];
        this.path = responseData['path'];
        this.value = responseData['value'];
        this.filter = responseData['filter'];
        this.colour = responseData['colour'];
        this.msg_kw = responseData['msg'];
        this.jsonfile = JSON.stringify(responseData);
      } catch (error) {
        console.log(error);
        this.errored = true;
        this.errorMessage = error.message;
      }
    },
    async get_chart(url) {
      try {
        const json_file = this.jsonfile;
        console.log('jsonfile: ', json_file)
        const responseData = await get_c(url, json_file);
        this.data = responseData['fig'].data
        this.layout = responseData['fig'].layout
        this.msg_chart = responseData['fig'].msg
      } catch (error) {
        console.log(error);
        this.errored = true;
        this.errorMessage = error.message;
      }
    },
    async generate_process(url1, url2) {
      this.loading_label = true;
      this.showaxis = false;
      await this.get_keyword(url1);
      this.get_chart(url2);
      this.loading_label = false;
      this.showaxis = true;
    },

  }
}
  ;
</script>
