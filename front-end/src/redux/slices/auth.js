import { createSlice } from "@reduxjs/toolkit";
import { dispatch } from "../store";

const initialState = {
  auth: {},
  isLogin: false,
};

const slice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginReducer(state, action) {
      state.auth = action.payload;
      state.isLogin = true;
    },
    logoutReducer(state, action) {
      state.isLogin = false;
      state.auth = {};
    },
  },
});

export const { loginReducer, logoutReducer } = slice.actions;

export default slice.reducer;
