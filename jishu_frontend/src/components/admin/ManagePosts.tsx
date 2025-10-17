import { useState, useEffect } from 'react';
import Header from '../Header';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../ui/alert-dialog';
import {
  Search,
  Eye,
  Trash2,
  MessageCircle,
  Heart,
  Flag,
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { adminApi } from '../../services/api';

interface ManagePostsProps {
  user: any;
}

export default function ManagePosts({ user }: ManagePostsProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState('posts');
  const [currentPage, setCurrentPage] = useState(1);
  const [perPage] = useState(10);

  // Posts state
  const [posts, setPosts] = useState<any[]>([]);
  const [postsPagination, setPostsPagination] = useState({ page: 1, pages: 1, total: 0, per_page: 10 });
  const [postsLoading, setPostsLoading] = useState(false);
  const [postsError, setPostsError] = useState<string | null>(null);

  // Comments state
  const [comments, setComments] = useState<any[]>([]);
  const [commentsPagination, setCommentsPagination] = useState({ page: 1, pages: 1, total: 0, per_page: 10 });
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [commentsError, setCommentsError] = useState<string | null>(null);

  // Deleted posts state
  const [deletedPosts, setDeletedPosts] = useState<any[]>([]);
  const [deletedPostsPagination, setDeletedPostsPagination] = useState({ page: 1, pages: 1, total: 0, per_page: 10 });
  const [deletedPostsLoading, setDeletedPostsLoading] = useState(false);
  const [deletedPostsError, setDeletedPostsError] = useState<string | null>(null);

  // Deleted comments state
  const [deletedComments, setDeletedComments] = useState<any[]>([]);
  const [deletedCommentsPagination, setDeletedCommentsPagination] = useState({ page: 1, pages: 1, total: 0, per_page: 10 });
  const [deletedCommentsLoading, setDeletedCommentsLoading] = useState(false);
  const [deletedCommentsError, setDeletedCommentsError] = useState<string | null>(null);

  // Fetch posts
  useEffect(() => {
    const fetchPosts = async () => {
      setPostsLoading(true);
      setPostsError(null);
      try {
        const response = await adminApi.getPosts(currentPage, perPage, searchQuery);
        setPosts(response.data?.posts || []);
        setPostsPagination(response.data?.pagination || { page: 1, pages: 1, total: 0, per_page: 10 });
      } catch (err: any) {
        setPostsError(err.message || 'Failed to fetch posts');
        toast.error('Failed to load posts');
      } finally {
        setPostsLoading(false);
      }
    };

    if (selectedTab === 'posts') {
      fetchPosts();
    }
  }, [currentPage, searchQuery, selectedTab, perPage]);

  // Fetch comments
  useEffect(() => {
    const fetchComments = async () => {
      setCommentsLoading(true);
      setCommentsError(null);
      try {
        const response = await adminApi.getComments(currentPage, perPage, searchQuery);
        setComments(response.data?.comments || []);
        setCommentsPagination(response.data?.pagination || { page: 1, pages: 1, total: 0, per_page: 10 });
      } catch (err: any) {
        setCommentsError(err.message || 'Failed to fetch comments');
        toast.error('Failed to load comments');
      } finally {
        setCommentsLoading(false);
      }
    };

    if (selectedTab === 'comments') {
      fetchComments();
    }
  }, [currentPage, searchQuery, selectedTab, perPage]);

  // Fetch deleted posts
  useEffect(() => {
    const fetchDeletedPosts = async () => {
      setDeletedPostsLoading(true);
      setDeletedPostsError(null);
      try {
        const response = await adminApi.getPosts(currentPage, perPage, searchQuery, '', true);
        setDeletedPosts(response.data?.posts || []);
        setDeletedPostsPagination(response.data?.pagination || { page: 1, pages: 1, total: 0, per_page: 10 });
      } catch (err: any) {
        setDeletedPostsError(err.message || 'Failed to fetch deleted posts');
        toast.error('Failed to load deleted posts');
      } finally {
        setDeletedPostsLoading(false);
      }
    };

    if (selectedTab === 'deleted') {
      fetchDeletedPosts();
    }
  }, [currentPage, searchQuery, selectedTab, perPage]);

  // Fetch deleted comments
  useEffect(() => {
    const fetchDeletedComments = async () => {
      setDeletedCommentsLoading(true);
      setDeletedCommentsError(null);
      try {
        const response = await adminApi.getComments(currentPage, perPage, searchQuery, true);
        setDeletedComments(response.data?.comments || []);
        setDeletedCommentsPagination(response.data?.pagination || { page: 1, pages: 1, total: 0, per_page: 10 });
      } catch (err: any) {
        setDeletedCommentsError(err.message || 'Failed to fetch deleted comments');
        toast.error('Failed to load deleted comments');
      } finally {
        setDeletedCommentsLoading(false);
      }
    };

    if (selectedTab === 'deleted-comments') {
      fetchDeletedComments();
    }
  }, [currentPage, searchQuery, selectedTab, perPage]);

  const handleDeletePost = async (postId: number) => {
    try {
      await adminApi.deletePost(postId);
      setPosts(posts.filter(post => post.id !== postId));
      toast.success('Post deleted successfully!');
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete post');
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    try {
      await adminApi.deleteComment(commentId);
      setComments(comments.filter(comment => comment.id !== commentId));
      toast.success('Comment deleted successfully!');
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete comment');
    }
  };

  const handlePageChange = (newPage: number) => {
    if (selectedTab === 'posts' && newPage >= 1 && newPage <= postsPagination.pages) {
      setCurrentPage(newPage);
    } else if (selectedTab === 'comments' && newPage >= 1 && newPage <= commentsPagination.pages) {
      setCurrentPage(newPage);
    } else if (selectedTab === 'deleted' && newPage >= 1 && newPage <= deletedPostsPagination.pages) {
      setCurrentPage(newPage);
    } else if (selectedTab === 'deleted-comments' && newPage >= 1 && newPage <= deletedCommentsPagination.pages) {
      setCurrentPage(newPage);
    }
  };

  return (
    <div className="min-h-screen bg-background dark:bg-slate-900">
      <Header user={user} />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-foreground">Manage Posts & Comments</h1>
          <p className="text-xl text-muted-foreground dark:text-muted-foreground">Moderate community content</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-1">Total Posts</p>
                  <p className="text-3xl text-foreground">{postsPagination.total}</p>
                </div>
                <MessageCircle className="w-10 h-10 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-1">Total Comments</p>
                  <p className="text-3xl text-foreground">{commentsPagination.total}</p>
                </div>
                <MessageCircle className="w-10 h-10 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-1">Total Likes</p>
                  <p className="text-3xl text-foreground">{posts.reduce((sum, p) => sum + (p.likes_count || 0), 0)}</p>
                </div>
                <Heart className="w-10 h-10 text-red-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-1">Deleted Items</p>
                  <p className="text-3xl text-red-600 dark:text-red-400">
                    {deletedPostsPagination.total + deletedCommentsPagination.total}
                  </p>
                </div>
                <Flag className="w-10 h-10 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 flex-wrap">
          <Button
            variant={selectedTab === 'posts' ? 'default' : 'outline'}
            onClick={() => {
              setSelectedTab('posts');
              setCurrentPage(1);
            }}
          >
            Posts
          </Button>
          <Button
            variant={selectedTab === 'comments' ? 'default' : 'outline'}
            onClick={() => {
              setSelectedTab('comments');
              setCurrentPage(1);
            }}
          >
            Comments
          </Button>
          <Button
            variant={selectedTab === 'deleted' ? 'default' : 'outline'}
            onClick={() => {
              setSelectedTab('deleted');
              setCurrentPage(1);
            }}
          >
            Deleted Posts
          </Button>
          <Button
            variant={selectedTab === 'deleted-comments' ? 'default' : 'outline'}
            onClick={() => {
              setSelectedTab('deleted-comments');
              setCurrentPage(1);
            }}
          >
            Deleted Comments
          </Button>
        </div>

        {/* Search */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search posts or comments..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Posts Table */}
        {selectedTab === 'posts' && (
          <Card>
            <CardHeader>
              <CardTitle>All Posts ({postsPagination.total})</CardTitle>
            </CardHeader>
            <CardContent>
              {postsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span>Loading posts...</span>
                </div>
              ) : postsError ? (
                <div className="text-center py-8 text-red-600">
                  <p>{postsError}</p>
                </div>
              ) : posts.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No posts found</p>
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Author</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Engagement</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {posts.map((post) => (
                        <TableRow key={post.id}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Avatar className="w-8 h-8">
                                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${post.user?.name}`} />
                                <AvatarFallback>{post.user?.name?.charAt(0) || 'U'}</AvatarFallback>
                              </Avatar>
                              <span className="text-sm">{post.user?.name || 'Unknown'}</span>
                            </div>
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <p className="truncate font-medium">{post.title}</p>
                            <p className="text-xs text-muted-foreground truncate">{post.content}</p>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-3 text-sm">
                              <span className="flex items-center gap-1">
                                <Heart className="w-4 h-4" /> {post.likes_count || 0}
                              </span>
                              <span className="flex items-center gap-1">
                                <MessageCircle className="w-4 h-4" /> {post.comments_count || 0}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>{new Date(post.created_at).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Badge
                              variant={post.is_deleted ? 'destructive' : post.status === 'published' ? 'default' : 'secondary'}
                            >
                              {post.is_deleted ? 'Deleted' : post.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button variant="ghost" size="sm">
                                <Eye className="w-4 h-4" />
                              </Button>
                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <Trash2 className="w-4 h-4 text-red-600" />
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Delete Post?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      This will soft delete "{post.title}". It will be hidden from users but can be recovered.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction onClick={() => handleDeletePost(post.id)}>
                                      Delete
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Pagination */}
                  <div className="flex items-center justify-between mt-6 pt-4 border-t">
                    <div className="text-sm text-muted-foreground">
                      Page {postsPagination.page} of {postsPagination.pages} ({postsPagination.total} total posts)
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="w-4 h-4" />
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === postsPagination.pages}
                      >
                        Next
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}

        {/* Comments Table */}
        {selectedTab === 'comments' && (
          <Card>
            <CardHeader>
              <CardTitle>All Comments ({commentsPagination.total})</CardTitle>
            </CardHeader>
            <CardContent>
              {commentsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span>Loading comments...</span>
                </div>
              ) : commentsError ? (
                <div className="text-center py-8 text-red-600">
                  <p>{commentsError}</p>
                </div>
              ) : comments.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No comments found</p>
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Author</TableHead>
                        <TableHead>Post</TableHead>
                        <TableHead>Comment</TableHead>
                        <TableHead>Likes</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {comments.map((comment) => (
                        <TableRow key={comment.id}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Avatar className="w-8 h-8">
                                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${comment.user?.name}`} />
                                <AvatarFallback>{comment.user?.name?.charAt(0) || 'U'}</AvatarFallback>
                              </Avatar>
                              <span className="text-sm">{comment.user?.name || 'Unknown'}</span>
                            </div>
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <p className="text-sm truncate">{comment.post?.title || 'Deleted Post'}</p>
                          </TableCell>
                          <TableCell className="max-w-sm">
                            <p className="text-sm truncate">{comment.content}</p>
                          </TableCell>
                          <TableCell>{comment.likes_count || 0}</TableCell>
                          <TableCell>{new Date(comment.created_at).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Badge variant={comment.is_deleted ? 'destructive' : 'default'}>
                              {comment.is_deleted ? 'Deleted' : 'Active'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <Trash2 className="w-4 h-4 text-red-600" />
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Delete Comment?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      This will soft delete this comment. It will be hidden from users but can be recovered.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction onClick={() => handleDeleteComment(comment.id)}>
                                      Delete
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Pagination */}
                  <div className="flex items-center justify-between mt-6 pt-4 border-t">
                    <div className="text-sm text-muted-foreground">
                      Page {commentsPagination.page} of {commentsPagination.pages} ({commentsPagination.total} total comments)
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="w-4 h-4" />
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === commentsPagination.pages}
                      >
                        Next
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}

        {/* Deleted Posts Table */}
        {selectedTab === 'deleted' && (
          <Card>
            <CardHeader>
              <CardTitle>Deleted Posts ({deletedPostsPagination.total})</CardTitle>
            </CardHeader>
            <CardContent>
              {deletedPostsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span>Loading deleted posts...</span>
                </div>
              ) : deletedPostsError ? (
                <div className="text-center py-8 text-red-600">
                  <p>{deletedPostsError}</p>
                </div>
              ) : deletedPosts.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No deleted posts found</p>
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Post ID</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Author</TableHead>
                        <TableHead>Likes</TableHead>
                        <TableHead>Comments</TableHead>
                        <TableHead>Deleted Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {deletedPosts.map((post) => (
                        <TableRow key={post.id}>
                          <TableCell>#{post.id}</TableCell>
                          <TableCell className="max-w-xs">
                            <p className="truncate">{post.title}</p>
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="text-sm">{post.user?.name}</p>
                              <p className="text-xs text-muted-foreground">{post.user?.email_id}</p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <Heart className="w-4 h-4 text-red-500" />
                              {post.likes_count}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <MessageCircle className="w-4 h-4 text-blue-500" />
                              {post.comments_count}
                            </div>
                          </TableCell>
                          <TableCell>
                            <p className="text-sm">{new Date(post.updated_at).toLocaleDateString()}</p>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Pagination */}
                  <div className="flex items-center justify-between mt-6 pt-4 border-t">
                    <div className="text-sm text-muted-foreground">
                      Page {deletedPostsPagination.page} of {deletedPostsPagination.pages} ({deletedPostsPagination.total} total deleted posts)
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="w-4 h-4" />
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === deletedPostsPagination.pages}
                      >
                        Next
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}

        {/* Deleted Comments Table */}
        {selectedTab === 'deleted-comments' && (
          <Card>
            <CardHeader>
              <CardTitle>Deleted Comments ({deletedCommentsPagination.total})</CardTitle>
            </CardHeader>
            <CardContent>
              {deletedCommentsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span>Loading deleted comments...</span>
                </div>
              ) : deletedCommentsError ? (
                <div className="text-center py-8 text-red-600">
                  <p>{deletedCommentsError}</p>
                </div>
              ) : deletedComments.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No deleted comments found</p>
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Comment ID</TableHead>
                        <TableHead>Author</TableHead>
                        <TableHead>Post</TableHead>
                        <TableHead>Content</TableHead>
                        <TableHead>Likes</TableHead>
                        <TableHead>Deleted Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {deletedComments.map((comment) => (
                        <TableRow key={comment.id}>
                          <TableCell>#{comment.id}</TableCell>
                          <TableCell>
                            <div>
                              <p className="text-sm">{comment.user?.name}</p>
                              <p className="text-xs text-muted-foreground">{comment.user?.email_id}</p>
                            </div>
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <p className="truncate text-sm">{comment.post?.title || 'Deleted Post'}</p>
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <p className="truncate text-sm">{comment.content}</p>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <Heart className="w-4 h-4 text-red-500" />
                              {comment.likes_count}
                            </div>
                          </TableCell>
                          <TableCell>
                            <p className="text-sm">{new Date(comment.updated_at).toLocaleDateString()}</p>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Pagination */}
                  <div className="flex items-center justify-between mt-6 pt-4 border-t">
                    <div className="text-sm text-muted-foreground">
                      Page {deletedCommentsPagination.page} of {deletedCommentsPagination.pages} ({deletedCommentsPagination.total} total deleted comments)
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="w-4 h-4" />
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === deletedCommentsPagination.pages}
                      >
                        Next
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
