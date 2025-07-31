import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

import backtestReducer from './slices/backtestSlice';
import optionsReducer from './slices/optionsSlice';
import portfolioReducer from './slices/portfolioSlice';

export const store = configureStore({
  reducer: {
    backtest: backtestReducer,
    options: optionsReducer,
    portfolio: portfolioReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
