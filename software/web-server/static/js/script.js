var socket = io();

socket.on('connect', function () {
    console.log('Connected to Socket.IO');
    socket.emit("subscribe")
});

const clock_store = Vue.reactive({
    time: 0,
    date: 0,
    progress: 0,
});
const spotify_store = Vue.reactive({
    now_playing: 0,
    title: 0,
    artists: 0,
    progress:0,
    cover_img:0,
})
const weather_store = Vue.reactive({
    condition: 0,
    condition_id: 0,
    code:0,
    description: 0,
    temp_c: 0,
    temp_min_c: 0,
    temp_max_c: 0,
    humidity: 0,
    wind: 0,
    dt: 0,
    sunrise: 0,
    sunset: 0,
    day:0,
})

socket.on('mqtt_message', function (data) {
// Handle MQTT messages here and update the HTML elements
    var topic = data.topic;
    var payload = data.payload;
    var payloadObj = JSON.parse(payload);

    // For demonstration, you can update a specific HTML element with the received data
    if (topic == "clock") {
        clock_store.time = payloadObj["time"];
        clock_store.date = payloadObj["date"];
    }
    else if (topic === 'spotify') {
        console.log(payloadObj)
        for (const key in payloadObj["current_playback"]) {
            if (spotify_store.hasOwnProperty(key)) {
                spotify_store[key] = payloadObj["current_playback"][key];
            }
        }
    }
    else if (topic == 'weather') {
         for (const key in payloadObj["current"]) {
            if (weather_store.hasOwnProperty(key)) {
                weather_store[key] = payloadObj["current"][key];
            }
        }
        clock_store.progress = payloadObj["current"]["progress"]
        console.log(clock_store)

    }

    //     document.getElementById('news_data').innerHTML = payload;
    // } else if (topic === 'spotify') {
    //     document.getElementById('spotify_data').innerHTML = payload;
    //     document.getElementById("spotify_cover").src = payloadObj["current_playback"]["cover_img"]
    // }
});


const clock = Vue.createApp({
    data(){
        return clock_store
    },
});
clock.mount('#clock')

const spotify = Vue.createApp({
    data(){
        return spotify_store
    },
});
spotify.mount('#spotify')

const weather = Vue.createApp({
    data(){
        return weather_store
    },
});
weather.mount('#weather')


