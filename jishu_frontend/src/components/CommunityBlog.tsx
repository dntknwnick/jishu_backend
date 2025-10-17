import { useState, useEffect } from 'react';
import Header from './Header';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import {
  Heart,
  MessageCircle,
  Share2,
  Plus,
  TrendingUp,
  Clock,
  Eye,
  Loader2,
  Send,
  Image as ImageIcon,
  Paperclip
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import { Label } from './ui/label';
import { toast } from 'sonner@2.0.3';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchPosts, createPost, likePost, addComment } from '../store/slices/communitySlice';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface CommunityBlogProps {
  user: any;
}

// Mock posts removed - now using Redux state

export default function CommunityBlog({ user }: CommunityBlogProps) {
  const dispatch = useAppDispatch();
  const { posts, isLoading, error } = useAppSelector((state) => state.community);

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newPost, setNewPost] = useState({ title: '', content: '', tags: '', image: null as File | null });
  const [commentInputs, setCommentInputs] = useState<{ [postId: number]: string }>({});
  const [showCommentInput, setShowCommentInput] = useState<{ [postId: number]: boolean }>({});
  const [expandedComments, setExpandedComments] = useState<{ [postId: number]: boolean }>({});

  useEffect(() => {
    dispatch(fetchPosts());
  }, [dispatch]);

  const toggleLike = async (postId: number) => {
    try {
      await dispatch(likePost(postId)).unwrap();
    } catch (error) {
      toast.error('Failed to like post');
    }
  };

  const toggleCommentInput = (postId: number) => {
    setShowCommentInput(prev => ({
      ...prev,
      [postId]: !prev[postId]
    }));
  };

  const handleCommentSubmit = async (postId: number) => {
    const content = commentInputs[postId]?.trim();
    if (!content) {
      toast.error('Please enter a comment');
      return;
    }

    try {
      await dispatch(addComment({ postId, content })).unwrap();
      setCommentInputs(prev => ({ ...prev, [postId]: '' }));
      setShowCommentInput(prev => ({ ...prev, [postId]: false }));
      toast.success('Comment added!');
    } catch (error) {
      toast.error('Failed to add comment');
    }
  };

  const handleCreatePost = async () => {
    if (!newPost.title || !newPost.content) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      const postData = {
        title: newPost.title,
        content: newPost.content,
        tags: newPost.tags.split(',').map(t => t.trim()).filter(t => t),
        image: newPost.image || undefined
      };

      await dispatch(createPost(postData)).unwrap();
      setNewPost({ title: '', content: '', tags: '', image: null });
      setIsCreateDialogOpen(false);
      toast.success('Post created successfully!');
    } catch (error) {
      toast.error('Failed to create post');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading posts...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background dark:bg-slate-900">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4 text-foreground">Error Loading Posts</h2>
            <p className="text-muted-foreground dark:text-muted-foreground mb-4">{error}</p>
            <Button onClick={() => dispatch(fetchPosts())}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background dark:bg-slate-900">
      <Header user={user} />

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2 text-foreground">Community Blog</h1>
            <p className="text-xl text-muted-foreground dark:text-muted-foreground">Share your journey, learn from others</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button size="lg" className="gap-2">
                <Plus className="w-5 h-5" />
                Create Post
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle className="text-foreground">Create a New Post</DialogTitle>
                <DialogDescription className="text-muted-foreground dark:text-muted-foreground">
                  Share your study tips, experiences, or ask questions to the community
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title" className="text-foreground">Title</Label>
                  <Input
                    id="title"
                    placeholder="Enter a catchy title"
                    value={newPost.title}
                    onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="content" className="text-foreground">Content</Label>
                  <Textarea
                    id="content"
                    placeholder="Share your thoughts..."
                    rows={6}
                    value={newPost.content}
                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tags" className="text-foreground">Tags (comma separated)</Label>
                  <Input
                    id="tags"
                    placeholder="e.g., NEET, Study Tips, Motivation"
                    value={newPost.tags}
                    onChange={(e) => setNewPost({ ...newPost, tags: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="image" className="text-foreground">Image (optional)</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="image"
                      type="file"
                      accept="image/*"
                      onChange={(e) => setNewPost({ ...newPost, image: e.target.files?.[0] || null })}
                      className="flex-1"
                    />
                    {newPost.image && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setNewPost({ ...newPost, image: null })}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                  {newPost.image && (
                    <p className="text-sm text-muted-foreground dark:text-muted-foreground">
                      Selected: {newPost.image.name}
                    </p>
                  )}
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreatePost}>Publish Post</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Feed */}
          <div className="lg:col-span-2 space-y-6">
            {posts.map((post) => (
              <Card key={post.id} className="overflow-hidden">
                {/* Post Header */}
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3 mb-4">
                    <Avatar className="w-10 h-10">
                      <AvatarImage src={post.author?.avatar} alt={post.author?.name} />
                      <AvatarFallback className="bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-200">
                        {post.author?.name?.charAt(0) || 'U'}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <h4 className="font-medium text-foreground">{post.author?.name || 'Anonymous'}</h4>
                      <p className="text-sm text-muted-foreground dark:text-muted-foreground">{post.author?.role || 'Student'}</p>
                    </div>
                    <span className="text-sm text-muted-foreground dark:text-muted-foreground flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {post.timeAgo}
                    </span>
                  </div>

                  {/* Post Content */}
                  <div className="space-y-3">
                    <h2 className="text-xl font-semibold text-foreground">
                      {post.title}
                    </h2>
                    <p className="text-foreground dark:text-muted-foreground leading-relaxed">{post.content}</p>

                    {/* Post Image */}
                    {(post.image_url || post.image) && (
                      <div className="mt-4">
                        <img
                          src={post.image_url || post.image}
                          alt={post.title}
                          className="w-full max-h-96 object-cover rounded-lg"
                          onError={(e) => {
                            // Hide image if it fails to load
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      </div>
                    )}

                    {/* Tags */}
                    {post.tags && post.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 pt-2">
                        {post.tags.map((tag, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  {/* Action Buttons */}
                  <div className="flex items-center justify-between py-3 border-t border-border">
                    <div className="flex items-center gap-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="gap-2 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400"
                        onClick={() => toggleLike(post.id)}
                      >
                        <Heart className={`w-5 h-5 ${post.is_liked ? 'fill-red-500 text-red-500' : ''}`} />
                        <span>{post.likes_count || 0}</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="gap-2 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-600 dark:hover:text-blue-400"
                        onClick={() => toggleCommentInput(post.id)}
                      >
                        <MessageCircle className="w-5 h-5" />
                        <span>{post.comments_count || 0}</span>
                      </Button>
                      <Button variant="ghost" size="sm" className="gap-2 hover:bg-gray-50 dark:hover:bg-gray-800">
                        <Share2 className="w-5 h-5" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground dark:text-muted-foreground">
                      <Eye className="w-4 h-4" />
                      <span>{post.views || 0}</span>
                    </div>
                  </div>

                  {/* Comments Section */}
                  {post.comments_count > 0 && (
                    <div className="space-y-3 py-3 border-t border-border">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium text-foreground dark:text-muted-foreground">
                          Comments ({post.comments_count})
                        </h4>
                        {post.comments_count > 3 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs text-blue-600 hover:text-blue-700"
                            onClick={() => setExpandedComments(prev => ({
                              ...prev,
                              [post.id]: !prev[post.id]
                            }))}
                          >
                            {expandedComments[post.id] ? 'Show Less' : `View All (${post.comments_count})`}
                          </Button>
                        )}
                      </div>

                      {/* Display comments */}
                      {post.recent_comments && post.recent_comments.length > 0 && (
                        <div className="space-y-3">
                          {post.recent_comments.map((comment) => (
                            <div key={comment.id} className="flex gap-3">
                              <Avatar className="w-8 h-8 flex-shrink-0">
                                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${comment.user?.name}`} />
                                <AvatarFallback className="bg-gray-100 text-muted-foreground text-xs">
                                  {comment.user?.name?.charAt(0) || 'U'}
                                </AvatarFallback>
                              </Avatar>
                              <div className="flex-1 min-w-0">
                                <div className="bg-gray-50 rounded-lg px-3 py-2">
                                  <p className="text-sm font-medium text-foreground">
                                    {comment.user?.name || 'Anonymous'}
                                  </p>
                                  <p className="text-sm text-foreground mt-1 break-words">{comment.content}</p>
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                  {new Date(comment.created_at).toLocaleDateString()}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Comment Input */}
                  {showCommentInput[post.id] && (
                    <div className="py-3 border-t border-gray-100">
                      <div className="flex gap-3">
                        <Avatar className="w-8 h-8">
                          <AvatarFallback className="bg-blue-100 text-blue-600 text-xs">
                            {user?.name?.charAt(0) || 'U'}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 space-y-2">
                          <Textarea
                            placeholder="Write a comment..."
                            value={commentInputs[post.id] || ''}
                            onChange={(e) => setCommentInputs(prev => ({
                              ...prev,
                              [post.id]: e.target.value
                            }))}
                            className="min-h-[80px] resize-none"
                          />
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setShowCommentInput(prev => ({
                                ...prev,
                                [post.id]: false
                              }))}
                            >
                              Cancel
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => handleCommentSubmit(post.id)}
                              disabled={!commentInputs[post.id]?.trim()}
                            >
                              Comment
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Trending Topics */}
            <Card>
              <CardHeader>
                <h3 className="text-lg flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Trending Topics
                </h3>
              </CardHeader>
              <CardContent className="space-y-3">
                {['NEET 2025', 'JEE Preparation', 'Study Techniques', 'Time Management', 'Motivation'].map((topic, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                    <span>#{topic}</span>
                    <Badge variant="secondary">{Math.floor(Math.random() * 50) + 10}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Popular Authors */}
            <Card>
              <CardHeader>
                <h3 className="text-lg">Popular Authors</h3>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { name: 'Dr. Amit Gupta', posts: '25', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Amit' },
                  { name: 'Sneha Reddy', posts: '18', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sneha' },
                  { name: 'Rohan Mehta', posts: '12', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rohan' },
                ].map((author, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <Avatar>
                      <AvatarImage src={author.avatar} alt={author.name} />
                      <AvatarFallback>{author.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <h4 className="text-sm">{author.name}</h4>
                      <p className="text-xs text-muted-foreground">{author.posts} posts</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Community Guidelines */}
            <Card className="bg-blue-50 border-blue-200">
              <CardHeader>
                <h3 className="text-lg">Community Guidelines</h3>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-foreground">
                <p>• Be respectful and supportive</p>
                <p>• Share authentic experiences</p>
                <p>• No spam or promotional content</p>
                <p>• Help others when you can</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
