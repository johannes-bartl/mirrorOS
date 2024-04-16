var socket = io();

socket.on('connect', function () {
    console.log('Connected to Socket.IO');
    socket.emit("subscribe")
});


const store = Vue.reactive({
    clock: {},
    current_weather: {},
    spotify: {},
    news: {}
});

socket.on('mqtt_message', function (data) {
// Handle MQTT messages here and update the HTML elements
    var topic = data.topic;
    var payload = data.payload;
    var payloadObj = JSON.parse(payload);

    // For demonstration, you can update a specific HTML element with the received data
    if (topic == "clock") {
        for (const key in payloadObj){
            store["clock"][key] = payloadObj[key];
        }
    }
    if (topic == "weather") {
        for (const key in payloadObj["current"]){
            store["current_weather"][key] = payloadObj["current"][key];
        }
    }
    if (topic === 'spotify') {
        for (const key in payloadObj["current_playback"]) {
            store["spotify"][key] = payloadObj["current_playback"][key];
        }
        console.log(store)
    }
    // else if (topic == 'weather') {
    //      for (const key in payloadObj["current"]) {
    //         if (weather_store.hasOwnProperty(key)) {
    //             weather_store[key] = payloadObj["current"][key];
    //         }
    //     }
    //     clock_store.progress = payloadObj["current"]["progress"]
    //     console.log(clock_store)
    //
    // }
    if (topic === 'news') {
        // console.log(payloadObj)
        for (const key in payloadObj) {
                store["news"][key] = payloadObj[key]
            }
    }
    //     document.getElementById('news_data').innerHTML = payload;
    // } else if (topic === 'spotify') {
    //     document.getElementById('spotify_data').innerHTML = payload;
    //     document.getElementById("spotify_cover").src = payloadObj["current_playback"]["cover_img"]
    // }
});

const header = Vue.createApp({
    data(){
        return store
    },
});
header.mount('.header')

const spotify = Vue.createApp({
    data(){
        return store
    },
});
spotify.mount('.spotify')

const news = Vue.createApp({
    data(){
        return store
    },
});
news.mount('.news')