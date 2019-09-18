document.addEventListener("DOMContentLoaded", () => {

  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  socket.on("connect", () => {

    socket.emit('joined');

    document.querySelector('#send-form').onsubmit = () => {
      let timestamp = new Date;
      timestamp = timestamp.toLocaleTimeString();
      let message = document.querySelector('input[name="message"]').value;
      socket.emit("submit message", {"message":message, "timestamp":timestamp});


      document.querySelector('input[name="message"]').value = "";
      return false;
    };

    document.querySelector("#back-home").onclick = () => {
      socket.emit("back home");
    }

    document.querySelector("#log-out").onclick = () => {
      socket.emit("back home");
    }
  });

  socket.on('status', data => {
    const li = document.createElement('li');
    li.innerHTML = `${data.msg}`;
    document.querySelector("#messages").append(li);
  })

  socket.on("announce message", data => {
    const li = document.createElement('li');
    li.innerHTML = `${data.message} `;
    document.querySelector("#messages").append(li);
  });
});
