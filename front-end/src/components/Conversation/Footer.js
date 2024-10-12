import { Box, Fab, IconButton, InputAdornment, Stack, TextField, Tooltip } from '@mui/material';
import React, { useEffect, useState } from 'react';
import { styled, useTheme } from "@mui/material/styles";
import { LinkSimple, PaperPlaneTilt, Smiley, Camera, File, Image, Sticker, User } from 'phosphor-react';
import data from '@emoji-mart/data'
import io from 'socket.io-client';
import Picker from '@emoji-mart/react'
import { useSelector } from 'react-redux';

const StyledInput = styled(TextField)(({ theme }) => ({
    "& .MuiInputBase-input": {
        paddingTop: '12px',
        paddingBottom: '12px',
    }
}));

const Actions = [
    {
        color: '#4da5fe',
        icon: <Image size={24} />,
        y: 102,
        title: 'Photo/Video'
    },
    {
        color: '#1b8cfe',
        icon: <Sticker size={24} />,
        y: 172,
        title: 'Stickers'
    },
    {
        color: '#0172e4',
        icon: <Camera size={24} />,
        y: 242,
        title: 'Image'
    },
    {
        color: '#0159b2',
        icon: <File size={24} />,
        y: 312,
        title: 'Document'
    },
    {
        color: '#013f7f',
        icon: <User size={24} />,
        y: 382,
        title: 'Contact'
    }
];

const ChatInput = ({ setOpenPicker, message, hanldeOnChange, handleKeyDown }) => {
    const [openAction, setOpenAction] = useState(false);

    return (
        <StyledInput fullWidth placeholder='Write a message...' onKeyDown={handleKeyDown} value={message} onChange={hanldeOnChange} variant='filled' InputProps={{
            disableUnderline: true,
            startAdornment:
                <Stack sx={{ width: 'max-content' }}>
                    <Stack sx={{ position: 'relative', display: openAction ? 'inline-block' : 'none' }}>
                        {Actions.map((el) => (
                            <Tooltip placement='right' title={el.title}>
                                <Fab sx={{ position: 'absolute', top: -el.y, backgroundColor: el.color }}>
                                    {el.icon}
                                </Fab>
                            </Tooltip>

                        ))}
                    </Stack>
                    <InputAdornment>
                        <IconButton onClick={() => {
                            setOpenAction((prev) => !prev)
                        }}>
                            <LinkSimple />
                        </IconButton>
                    </InputAdornment>
                </Stack>
            ,
            endAdornment: <InputAdornment>
                <IconButton onClick={() => {
                    setOpenPicker((prev) => !prev);
                }}>
                    <Smiley />
                </IconButton>
            </InputAdornment>
        }} />
    )
}

const Footer = () => {
    const theme = useTheme();
    const [openPicker, setOpenPicker] = useState(false);
    const [message, setMessage] = useState("");
    const [socket, setSocket] = useState(null);
    const [messages, setMessages] = useState([]);
    const { chats } = useSelector((state) => state?.chats);


    const hanldeOnChange = (e) => {
        setMessage(e.target.value)
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            handleMessage(message);
        }
    };

    useEffect(() => {
        const auth = JSON.parse(localStorage.getItem('auth'));

        const ws = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${chats?.name}/?token=${auth?.token?.access}`);
        setSocket(ws);

        ws.onopen = () => {
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMessages((prevMessages) => [...prevMessages, data.message]);
            console.log('MESSAGE send');
            console.log({ data });
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
        };

        return () => {
            ws.close();
        };
    }, [chats?.id])

    const handleMessage = (message) => {
        if (socket) {
            const messageData = JSON.stringify({ message });
            socket.send(messageData); // Send message to WebSocket
            setMessage('');
        }
    };


    return (
        <Box p={2} sx={{
            width: '100%', backgroundColor: theme.palette.mode === 'light' ? '#F8FAFF' :
                theme.palette.background.paper, boxShadow: '0px 0px 2px rgba(0,0,0,0.25)'
        }}>
            <Stack direction='row' alignItems={'center'} spacing={3}>

                <Stack sx={{ width: '100%' }}>
                    {/* Chat Input */}
                    <Box sx={{ display: openPicker ? 'inline' : 'none', zIndex: 10, position: 'fixed', bottom: 81, right: 100 }}>
                        <Picker theme={theme.palette.mode} data={data} onEmojiSelect={console.log} />
                    </Box>
                    <ChatInput
                        setOpenPicker={setOpenPicker}
                        hanldeOnChange={hanldeOnChange}
                        onKeyDown={handleKeyDown}
                        message={message} />
                </Stack>

                <Box sx={{
                    height: 48, width: 48, backgroundColor: theme.palette.primary.main,
                    borderRadius: 1.5
                }}
                    onClick={() => handleMessage(message)}>
                    <Stack sx={{ height: '100%', width: '100%', alignItems: 'center', justifyContent: 'center' }}>
                        <IconButton>
                            <PaperPlaneTilt color='#fff' />
                        </IconButton>
                    </Stack>

                </Box>
            </Stack>
        </Box>
    )
}

export default Footer