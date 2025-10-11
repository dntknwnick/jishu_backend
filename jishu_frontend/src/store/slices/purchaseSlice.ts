import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

interface Purchase {
  id: number;
  userId: number;
  courseId: string;
  courseName: string;
  items: any[];
  amount: number;
  date: string;
  status: string;
}

interface PurchaseState {
  purchases: Purchase[];
  currentCart: {
    items: any[];
    courseId: string | null;
    courseName: string | null;
    isBundle: boolean;
    bundleDiscount: number;
  };
  isLoading: boolean;
  error: string | null;
}

const initialState: PurchaseState = {
  purchases: [],
  currentCart: {
    items: [],
    courseId: null,
    courseName: null,
    isBundle: false,
    bundleDiscount: 0,
  },
  isLoading: false,
  error: null,
};

// For now, we'll use localStorage for purchases until backend payment integration
export const processPurchase = createAsyncThunk(
  'purchase/processPurchase',
  async (
    purchaseData: {
      userId: number;
      courseId: string;
      courseName: string;
      items: any[];
      amount: number;
      paymentMethod: string;
      paymentDetails: any;
    },
    { rejectWithValue }
  ) => {
    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const purchase: Purchase = {
        id: Date.now(),
        userId: purchaseData.userId,
        courseId: purchaseData.courseId,
        courseName: purchaseData.courseName,
        items: purchaseData.items,
        amount: purchaseData.amount,
        date: new Date().toISOString(),
        status: 'completed',
      };

      // Store in localStorage for now
      const purchases = JSON.parse(localStorage.getItem('jishu_purchases') || '[]');
      purchases.push(purchase);
      localStorage.setItem('jishu_purchases', JSON.stringify(purchases));

      return purchase;
    } catch (error) {
      return rejectWithValue('Payment processing failed');
    }
  }
);

export const loadPurchases = createAsyncThunk(
  'purchase/loadPurchases',
  async (userId: number, { rejectWithValue }) => {
    try {
      const purchases = JSON.parse(localStorage.getItem('jishu_purchases') || '[]');
      return purchases.filter((p: Purchase) => p.userId === userId);
    } catch (error) {
      return rejectWithValue('Failed to load purchases');
    }
  }
);

const purchaseSlice = createSlice({
  name: 'purchase',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCart: (state, action) => {
      state.currentCart = action.payload;
    },
    clearCart: (state) => {
      state.currentCart = {
        items: [],
        courseId: null,
        courseName: null,
        isBundle: false,
        bundleDiscount: 0,
      };
    },
    addToCart: (state, action) => {
      const item = action.payload;
      const existingIndex = state.currentCart.items.findIndex(i => i.id === item.id);
      if (existingIndex === -1) {
        state.currentCart.items.push(item);
      }
    },
    removeFromCart: (state, action) => {
      const itemId = action.payload;
      state.currentCart.items = state.currentCart.items.filter(i => i.id !== itemId);
    },
  },
  extraReducers: (builder) => {
    builder
      // Process purchase
      .addCase(processPurchase.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(processPurchase.fulfilled, (state, action) => {
        state.isLoading = false;
        state.purchases.push(action.payload);
        // Clear cart after successful purchase
        state.currentCart = {
          items: [],
          courseId: null,
          courseName: null,
          isBundle: false,
          bundleDiscount: 0,
        };
      })
      .addCase(processPurchase.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Load purchases
      .addCase(loadPurchases.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadPurchases.fulfilled, (state, action) => {
        state.isLoading = false;
        state.purchases = action.payload;
      })
      .addCase(loadPurchases.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  clearError,
  setCart,
  clearCart,
  addToCart,
  removeFromCart,
} = purchaseSlice.actions;
export default purchaseSlice.reducer;
