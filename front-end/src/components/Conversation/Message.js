import { Box, Stack } from '@mui/material'
import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import io from 'socket.io-client';
import { Chat_History } from '../../data'
import { DocMsg, LinkMsg, MediaMsg, ReplyMsg, TextMsg, TimeLine } from './MsgTypes';
import axiosInstance from '../../utils/axiosInstance';


const Message = ({ menu }) => {
  const { chats } = useSelector((state) => state?.chats);
  const [messages, setMessages] = useState([]);

  // console.log(chats);

  const fetchMessages = async () => {
    try {
      let response = await axiosInstance.get(`/messages/get/${chats?.name}/chats/`)
      // console.log(response);
      setMessages(response?.data?.results)
    } catch (error) {
      console.log(error);
    }
  }

  useEffect(() => {
    fetchMessages()
  }, [chats?.id])

  return (
    <Box p={3}>
      <Stack spacing={3}>
        {messages?.map((i, index) => (
          <TextMsg key={index} data={i} />
        ))}
        {/* {Chat_History.map((el) => {
          switch (el.type) {
            case 'divider':
              return <TimeLine el={el} />

            case 'msg':
              switch (el.subtype) {
                case 'img':
                return <MediaMsg el={el} menu={menu} />
                case 'doc':
                return <DocMsg el={el} menu={menu} />
                case 'link':
                return <LinkMsg el={el} menu={menu} />
                case 'reply':
                return <ReplyMsg el={el} menu={menu} />
                default:
                  return <TextMsg el={el} menu={menu} />
              }
              break;

            default:
              return <></>;
          }
        })} */}
      </Stack>
    </Box>
  )
}

export default Message