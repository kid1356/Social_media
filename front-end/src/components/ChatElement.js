import { Avatar, Badge, Box, Stack, Typography } from '@mui/material';
import { useTheme, styled } from '@mui/material/styles';
import StyledBadge from './StyledBadge';

//single chat element
const ChatElement = ({ data, img, online, onClick }) => {

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  const theme = useTheme();
  return (
    <Box onClick={() => onClick(data)} sx={{
      width: "100%",
      borderRadius: 1,
      backgroundColor: theme.palette.mode === 'light' ? "#fff" : theme.palette.background.default

    }}
      p={2}>
      <Stack direction="row" alignItems='center' justifyContent='space-between'>
        <Stack direction='row' spacing={2}>
          {online ? <StyledBadge overlap='circular' anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            variant="dot">
            {/* <Avatar src={`http://localhost:8000/media/${data?.participants[0]?.profile_picture || img}`} /> */}
            <Avatar src={`${data?.participants[0]?.profile_picture}`} />
          </StyledBadge> : <Avatar src={img} />}

          <Stack spacing={0.3}>
            <Typography variant='subtitle2'>
              {data?.room_type === "group" ? data?.name : data?.participants[0].first_name}
            </Typography>
            <Typography variant='caption'>
              {data?.last_message}
            </Typography>
          </Stack>
        </Stack>
        <Stack spacing={2} alignItems='center'>
          <Typography sx={{ fontWeight: 600 }} variant='caption'>
            {formatTime(data?.last_message_time)}
          </Typography>
          <Badge color='primary' badgeContent={data?.unread}>

          </Badge>
        </Stack>


      </Stack>


    </Box>
  )
};

export default ChatElement