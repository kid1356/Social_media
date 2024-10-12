import { createSlice } from "@reduxjs/toolkit";
import { dispatch } from "../store";

const initialState = {
    chats: [],
    selectedChatId: null,
};

const slice = createSlice({
    name: 'chats',
    initialState,
    reducers: {
        setChats(state, action) {
            state.chats = action.payload;
        },
    }
});

export default slice.reducer;

export function setNewChat(chat) {
    dispatch(slice.actions.setChats(chat));
}