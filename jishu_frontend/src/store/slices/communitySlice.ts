import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { communityApi, BlogPost, ApiError } from '../../services/api';

interface CommunityState {
  posts: BlogPost[];
  isLoading: boolean;
  error: string | null;
}

const initialState: CommunityState = {
  posts: [],
  isLoading: false,
  error: null,
};

// Helper function to transform backend post data to frontend format
const transformPost = (post: any): BlogPost => {
  const timeAgo = new Date(post.created_at).toLocaleDateString();

  return {
    ...post,
    author: {
      name: post.user?.name || 'Anonymous',
      avatar: '', // No avatar in backend yet
      role: 'Student' // Default role
    },
    timeAgo,
    likes: post.likes_count,
    comments: post.comments_count,
    views: Math.floor(Math.random() * 1000) + 100, // Mock views for now
    image: post.image_url // Map image_url to image for backward compatibility
  };
};

// Async thunks
export const fetchPosts = createAsyncThunk(
  'community/fetchPosts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await communityApi.getPosts();
      const posts = response.data?.posts || [];
      return posts.map(transformPost);
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch posts');
    }
  }
);

export const createPost = createAsyncThunk(
  'community/createPost',
  async (
    data: { title: string; content: string; tags: string[]; image?: File },
    { rejectWithValue }
  ) => {
    try {
      const response = await communityApi.createPost(data);
      const post = response.data?.post;
      return post ? transformPost(post) : null;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to create post');
    }
  }
);

export const likePost = createAsyncThunk(
  'community/likePost',
  async (postId: number, { rejectWithValue }) => {
    try {
      const response = await communityApi.likePost(postId);
      return {
        postId,
        liked: response.data?.liked,
        likes_count: response.data?.likes_count
      };
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to like post');
    }
  }
);

export const addComment = createAsyncThunk(
  'community/addComment',
  async ({ postId, content }: { postId: number; content: string }, { rejectWithValue }) => {
    try {
      const response = await communityApi.addComment(postId, content);
      return { postId, comment: response.data };
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to add comment');
    }
  }
);

export const deletePost = createAsyncThunk(
  'community/deletePost',
  async (postId: number, { rejectWithValue }) => {
    try {
      await communityApi.deletePost(postId);
      return postId;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to delete post');
    }
  }
);

const communitySlice = createSlice({
  name: 'community',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    togglePostLike: (state, action) => {
      const postId = action.payload;
      const post = state.posts.find(p => p.id === postId);
      if (post) {
        post.is_liked = !post.is_liked;
        post.likes_count += post.is_liked ? 1 : -1;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch posts
      .addCase(fetchPosts.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPosts.fulfilled, (state, action) => {
        state.isLoading = false;
        state.posts = action.payload;
      })
      .addCase(fetchPosts.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Create post
      .addCase(createPost.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createPost.fulfilled, (state, action) => {
        state.isLoading = false;
        if (action.payload) {
          state.posts.unshift(action.payload);
        }
      })
      .addCase(createPost.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Like post
      .addCase(likePost.fulfilled, (state, action) => {
        const { postId, liked, likes_count } = action.payload;
        const post = state.posts.find(p => p.id === postId);
        if (post) {
          post.is_liked = liked;
          post.likes_count = likes_count;
        }
      })
      .addCase(likePost.rejected, (state, action) => {
        state.error = action.payload as string;
      })

      // Add comment
      .addCase(addComment.fulfilled, (state, action) => {
        const { postId, comment } = action.payload;
        const post = state.posts.find(p => p.id === postId);
        if (post) {
          post.comments_count += 1;
          // Add comment to recent_comments if it exists
          if (post.recent_comments) {
            post.recent_comments.unshift(comment);
            // Keep only the 3 most recent comments
            if (post.recent_comments.length > 3) {
              post.recent_comments = post.recent_comments.slice(0, 3);
            }
          }
        }
      })
      .addCase(addComment.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      
      // Delete post
      .addCase(deletePost.fulfilled, (state, action) => {
        const postId = action.payload;
        state.posts = state.posts.filter(p => p.id !== postId);
      })
      .addCase(deletePost.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const { clearError, togglePostLike } = communitySlice.actions;
export default communitySlice.reducer;
