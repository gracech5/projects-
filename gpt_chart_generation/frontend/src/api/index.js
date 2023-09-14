import axios from "axios";

let port = process.env.VUE_APP_BACKEND_PORT;
let mode = process.env.VUE_APP_MODE;

console.log('process.env: ', process.env);

if (typeof port == 'undefined' | !port) {
    port = 8000;
}

let baseURL = `http://localhost:${port}`
if (mode == 'PROD') {
    // for DGX deployment
    baseURL = `http://sggpu00.sin.sap.corp:${port}`;
} else if (mode == 'DEV') {
    // for localhost docker deployment
    baseURL = `http://localhost:${port}`;
}
console.log('baseURL: ', baseURL);


const instance = axios.create({
    baseURL: baseURL,
    headers: {
        "Content-Type": "application/json",
    },
});


export const performLogin = async (username, password) => {
    let authenticated = false; // default value
    if (username != "" && password != "") {
        const payload = {
            username: username,
            password: password
        };

        try {
            const response = await instance.post('/authentication', null, {params: payload});
            authenticated = response.data;
            console.log('response: ', authenticated);
        } catch (error) {
            console.log(error);
        }
    } else {
        console.log("A username and password must be present");
    }
    return authenticated;
};

export const get_kw = async(url, user_input) => {
    // console.log('payload: ', payload)
    const new_url = `${url}?user_input=${encodeURIComponent(user_input)}`;
    const response = await instance.post(new_url);
    console.log('Response: ', response)
    return response.data
};

export const get_c = async(url, request) => {
    // console.log('payload: ', payload)
    const response = await instance.post(url,request);
    console.log('Response: ', response)
    return response.data
};
