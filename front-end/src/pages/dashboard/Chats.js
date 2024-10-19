import { Box, IconButton, Stack, Typography, InputBase, Button, Divider, Avatar, Badge } from
  '@mui/material'
import { ArchiveBox, CircleDashed, MagnifyingGlass } from 'phosphor-react';
import { useTheme } from '@mui/material/styles';
import React, { useEffect, useState } from 'react';
import { faker } from '@faker-js/faker';
import { ChatList } from '../../data';
import { Search, SearchIconWrapper, StyledInputBase } from '../../components/Search';
import ChatElement from '../../components/ChatElement';
import axiosInstance from '../../utils/axiosInstance';
import { setNewChat } from '../../redux/slices/chats';
import getUserAllChatsRoom from '../../json/getUserAllChatsRoom.json';

const Chats = () => {
  const theme = useTheme();
  const [chatRoom, setChatRoom] = useState([]);

  const fetchChatRooms = async () => {
    try {
      const response = await axiosInstance.get('/messages/get-user-all-chat-rooms?room_type=private');
      setChatRoom(response?.data?.results)
      // setChatRoom(getUserAllChatsRoom)
    } catch (error) {
      console.log(error);
    }
  }

  const handleOnClick = (data) => {
    setNewChat(data)
  }

  useEffect(() => {
    handleOnClick(chatRoom[0])
  }, [chatRoom])

  useEffect(() => {
    fetchChatRooms()
  }, [])

  return (
    <Box sx={{
      position: "relative", width: 320,
      backgroundColor: theme.palette.mode === 'light' ? "#F8FAFF" : theme.palette.background.paper,
      boxShadow: '0px 0px 2px rgba(0,0,0,0.25)'
    }}>
      <Stack p={3} spacing={2} sx={{ height: "100vh" }}>
        <Stack direction="row" alignItems='center' justifyContent='space-between'>
          <Typography variant='h5'>
            Chats
          </Typography>
          <IconButton>
            <CircleDashed />
          </IconButton>
        </Stack>

        <Stack sx={{ width: "100%" }}>
          <Search>
            <SearchIconWrapper>
              <MagnifyingGlass color="#709CE6" />
            </SearchIconWrapper>
            <StyledInputBase placeholder='Search...' inputProps={{ "aria-label": "search" }} />
          </Search>
        </Stack>

        {/* <Stack spacing={1}>
          <Stack direction='row' alignItems='center' spacing={1.5}>
            <ArchiveBox size={24} />
            <Button>
              Archive
            </Button>
          </Stack>
          <Divider />
        </Stack> */}

        <Stack className='scrollbar' spacing={2} direction='column' sx={{ flexGrow: 1, overflow: 'scroll', height: '100%' }}>

          {/* <Stack spacing={2.4}>
              <Typography variant='subtitle2' sx={{color:"#676767"}}>
                Pinned
              </Typography>
              {ChatList.filter((el)=> el.pinned).map((el)=>{
                return <ChatElement  {...el}/>
              })}
              
            </Stack> */}

          <Stack spacing={2.4}>
            <Typography variant='subtitle2' sx={{ color: "#676767" }}>
              All Chats
            </Typography>
            {chatRoom.filter((el) => !el.pinned).map((el, index) => {
              return <ChatElement key={index} {...el} data={el} onClick={handleOnClick} />
            })}

          </Stack>

        </Stack>
      </Stack>

    </Box>
  )
}

export default Chats