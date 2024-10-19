import { Box, Stack } from "@mui/material";
import { useSelector } from "react-redux";
import React, { useEffect, useRef, useState } from "react";
import { useTheme } from "@mui/material/styles";
import Header from "./Header";
import Footer from "./Footer";
import Message from "./Message";
import axiosInstance from "../../utils/axiosInstance";
// import messagesJson from "../../json/messages.json";

const Conversation = () => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageValue, setMessageValue] = useState("");
  const chatEndRef = useRef(null);

  const { auth } = useSelector((state) => state?.auth);
  const { chats } = useSelector((state) => state?.chats);

  const theme = useTheme();

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  useEffect(() => {
    if (chats?.id) {
      fetchMessageHistory();
      handleSocketConnection();
    }
  }, [chats?.id]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMessageHistory = async () => {
    try {
      let response = await axiosInstance.get(`/messages/get/${chats?.name}/chats/`)
      setMessages(response?.data?.results)
      // setMessages(messages);
    } catch (error) {
      console.log(error);
    }
  };

  const handleMessage = (message) => {

    if (socket) {
      const messageData = JSON.stringify({ message });
      socket.send(messageData);
    }
    setMessageValue("");
  };

  const hanldeOnChange = (e) => {
    setMessageValue(e.target.value);
  };

  const handleSocketConnection = () => {
    if (socket) {
      console.log("WebSocket already exists");
      return; 
    }

    const ws = new WebSocket(
      `ws://127.0.0.1:8000/ws/chat/${chats?.name}/?token=${auth?.token?.access}`
    );
    setSocket(ws);
    ws.onopen = () => {
      console.log("WebSocket connected");
    };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prevMessages) => [{ ...data.message, receiver: data?.receiver, receiver_name: data?.receiver_name }, ...prevMessages]);
      console.log("MESSAGE send");
      console.log({data});
      
    };
    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };
    return () => {
      ws.close();
    };
  };

  return (
    <Stack height={"100%"} maxHeight={"100vh"} width={"auto"}>
      {/* ================ Chat header ================ */}
      <Header />

      {/* ================ Msg ================ */}
      <Box
        className="scrollbar"
        width={"100%"}
        sx={{ flexGrow: 1, height: "100%", overflowY: "scroll" }}
      >
        <Message menu={true} messages={messages} />
        <div ref={chatEndRef} />
      </Box>

      {/* ================ Chat footer ================ */}
      <Footer
        messageValue={messageValue}
        hanldeOnChange={hanldeOnChange}
        handleMessage={handleMessage}
      />
    </Stack>
  );
};

export default Conversation;
