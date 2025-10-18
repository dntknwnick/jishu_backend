# 🗺️ Navigation Guide - Jishu Mobile App

## 📱 App Structure Overview

```
┌─────────────────────────────────────────┐
│         JISHU MOBILE APP                │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Authentication Flow              │ │
│  │  ├─ Welcome Screen                │ │
│  │  ├─ Login (OTP)                   │ │
│  │  ├─ Register                      │ │
│  │  └─ OTP Verification              │ │
│  └───────────────────────────────────┘ │
│                 ↓                       │
│  ┌───────────────────────────────────┐ │
│  │  Main App (Drawer + Bottom Tabs) │ │
│  │                                   │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │  Hamburger Drawer Menu      │ │ │
│  │  │  ├─ 👤 My Profile           │ │ │
│  │  │  ├─ ✏️ Edit Profile         │ │ │
│  │  │  ├─ ⚙️ Settings              │ │ │
│  │  │  ├─ 🔔 Notifications        │ │ │
│  │  │  ├─ 🔖 Bookmarks            │ │ │
│  │  │  ├─ ❓ Help                  │ │ │
│  │  │  ├─ ℹ️ About                 │ │ │
│  │  │  └─ 🚪 Logout               │ │ │
│  │  └─────────────────────────────┘ │ │
│  │                                   │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │  Bottom Tab Navigation      │ │ │
│  │  │  ┌─────┬─────┬─────┬─────┬─┐│ │
│  │  │  │ 🏠  │ 📚  │ 📝  │ 👥  │🤖││ │
│  │  │  │Home │Cours│Tests│Comm │AI││ │
│  │  │  │     │ es  │     │unity│  ││ │
│  │  │  └─────┴─────┴─────┴─────┴─┘│ │
│  │  └─────────────────────────────┘ │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🏠 Bottom Tab Navigation

### Tab 1: Home (Dashboard)
**Icon:** 🏠 `home` / `home-outline`

**Features:**
- User stats (tests taken, avg score, study streak, rank)
- Quick actions (Start Test, My Courses, Practice, AI Chatbot)
- Recent test results
- Study analytics
- Daily goals

**Header:**
- Hamburger menu icon (opens drawer)
- Notification bell icon

---

### Tab 2: Courses
**Icon:** 📚 `book` / `book-outline`

**Features:**
- Enrolled courses grid
- Course progress indicators
- Subject filters (All, Physics, Chemistry, Biology, Mathematics)
- Search functionality
- Course details on tap

**Available Courses:**
- NEET Complete Bundle
- JEE Advanced Complete
- CET Physics
- NEET Biology

---

### Tab 3: Tests
**Icon:** 📝 `document-text` / `document-text-outline`

**Features:**
- Available tests list
- Completed tests
- Test categories (Subject-wise, Full-length, Topic-wise, Previous Year)
- Test details (questions, duration, marks)
- Start/Resume test functionality

**Test Info:**
- Number of questions
- Time duration
- Total marks
- Completion status

---

### Tab 4: Community
**Icon:** 👥 `people` / `people-outline`

**Features:**
- Discussion posts feed
- Post creation
- Like/comment on posts
- User avatars
- Post timestamps
- Search posts
- Filter by category

**Post Types:**
- Questions
- Study tips
- Exam experiences
- Motivational content

---

### Tab 5: Chatbot (AI Assistant) ⭐ NEW!
**Icon:** 🤖 `chatbubbles` / `chatbubbles-outline`

**Features:**
- AI-powered chat interface
- Quick question suggestions
- Message history
- Typing indicator
- Auto-scroll to latest message
- Keyboard-aware layout

**Quick Questions:**
- "Explain Newton's Laws"
- "Organic Chemistry basics"
- "Human anatomy"
- "Physics formulas"

**Chat Features:**
- User messages (blue bubbles, right-aligned)
- Bot messages (white bubbles, left-aligned)
- Timestamps on each message
- Message input with send button
- Online status indicator
- AI avatar icon

---

## 🍔 Drawer Menu (Hamburger)

### Accessed From:
- Tap hamburger icon (☰) on Home screen header
- Swipe from left edge of screen

### Menu Items:

#### 1. 👤 My Profile ⭐ NEW LOCATION!
**Previously in bottom tabs, now in drawer**

**Features:**
- User avatar and name
- Email address
- Stats overview (Tests, Accuracy, Rank)
- Achievement badges
- Recent activity
- Progress charts

---

#### 2. ✏️ Edit Profile
**Edit user information**

**Can Edit:**
- Name
- Email
- Phone number
- Profile picture
- Bio
- Preferences

---

#### 3. ⚙️ Account Settings
**Account preferences and configuration**

**Settings:**
- Notification preferences
- Language selection
- Theme settings
- Privacy settings
- Data management

---

#### 4. 🔔 Notifications
**Notification center**

**Types:**
- New test available
- Course updates
- Community interactions
- Reminders
- Achievements

---

#### 5. 🔖 Bookmarks
**Saved content**

**Bookmarkable Items:**
- Important questions
- Community posts
- Study materials
- Test results
- Notes

---

#### 6. ❓ Help & Support
**Get help and support**

**Sections:**
- FAQs
- Contact support
- Report issue
- Feature requests
- User guide

---

#### 7. ℹ️ About
**App information**

**Content:**
- App version
- Terms of service
- Privacy policy
- Credits
- Open source licenses

---

#### 8. 🚪 Logout
**Sign out of the app**

**Action:**
- Shows confirmation dialog
- Clears user session
- Returns to Welcome screen

---

## 🔄 Navigation Flow

### User Journey:

```
1. App Launch
   ↓
2. Welcome Screen
   ↓
3. Login/Register
   ↓
4. OTP Verification
   ↓
5. Home Screen (Bottom Tabs)
   ├─ Can navigate to any tab
   └─ Can open drawer menu
      ├─ Access Profile
      └─ Access Settings/Help/etc
```

### Tab Switching:
```
Home ←→ Courses ←→ Tests ←→ Community ←→ Chatbot
  │         │         │         │           │
  └─────────┴─────────┴─────────┴───────────┘
              All tabs accessible anytime
```

### Drawer Access:
```
Any Screen
   ↓
Tap ☰ or Swipe Right
   ↓
Drawer Opens
   ↓
Select Menu Item
   ↓
Navigate to Screen
   ↓
Tap Back or Close
   ↓
Return to Previous Screen
```

---

## 🎯 Key Navigation Patterns

### Bottom Tabs (Main Navigation):
- **Always Visible**: Bottom tabs are always accessible
- **Direct Access**: Tap any tab to switch immediately
- **Active Indicator**: Current tab is highlighted
- **Icon States**: Filled icon for active, outline for inactive

### Drawer Menu (Secondary Navigation):
- **Swipe or Tap**: Open via hamburger icon or swipe from left
- **Overlay**: Drawer slides over content
- **Close Methods**: 
  - Tap outside drawer
  - Tap X button
  - Navigate to screen
  - Swipe left

### Stack Navigation (Screen Flow):
- **Linear Flow**: Authentication screens are sequential
- **Back Button**: Navigate back through stack
- **Header**: Shows on most screens with back button

---

## 📱 Screen Headers

### Home Screen:
```
┌─────────────────────────────────┐
│ ☰  Dashboard            🔔      │
└─────────────────────────────────┘
```

### Courses Screen:
```
┌─────────────────────────────────┐
│ ←  My Courses                   │
└─────────────────────────────────┘
```

### Tests Screen:
```
┌─────────────────────────────────┐
│ ←  Mock Tests                   │
└─────────────────────────────────┘
```

### Community Screen:
```
┌─────────────────────────────────┐
│ ←  Community                    │
└─────────────────────────────────┘
```

### Chatbot Screen:
```
┌─────────────────────────────────┐
│ 🤖 AI Study Assistant           │
│    Ask me anything!    ● Online │
└─────────────────────────────────┘
```

### Profile Screen (from Drawer):
```
┌─────────────────────────────────┐
│ ←  My Profile                   │
└─────────────────────────────────┘
```

---

## 🎨 Visual Design

### Color Scheme:
- **Primary**: `#6366f1` (Indigo)
- **Secondary**: `#8b5cf6` (Purple)
- **Success**: `#10b981` (Green)
- **Warning**: `#f59e0b` (Orange)
- **Error**: `#ef4444` (Red)
- **Background**: `#f9fafb` (Light Gray)
- **Text**: `#1f2937` (Dark Gray)

### Tab Bar:
- **Active Color**: `#6366f1` (Indigo)
- **Inactive Color**: `#9ca3af` (Gray)
- **Background**: `#ffffff` (White)
- **Height**: 60px (Android), 85px (iOS with safe area)

### Drawer:
- **Width**: 280px
- **Background**: `#ffffff` (White)
- **Profile Section**: Gradient background `#6366f1` → `#8b5cf6`

---

## 🔍 Navigation Tips

### Best Practices:
1. **Use Bottom Tabs** for frequently accessed screens
2. **Use Drawer** for settings and profile
3. **Chatbot** is always one tap away
4. **Back Button** works consistently across all screens
5. **Gestures** work on both iOS and Android

### Gestures:
- **Swipe Right**: Open drawer (from left edge)
- **Swipe Left**: Close drawer
- **Swipe Down**: Refresh content (on some screens)
- **Tap Outside**: Close drawer/modals

---

## 🚀 Quick Actions

### From Home Screen:
- **Start Test**: Opens test selection
- **My Courses**: Goes to Courses tab
- **Practice**: Opens practice mode
- **AI Chatbot**: Goes to Chatbot tab

### From Any Tab:
- **Hamburger Menu**: Access profile and settings
- **Tab Bar**: Switch between main screens
- **Back Button**: Return to previous screen

---

## 📝 Notes

- All screens are fully responsive
- Navigation works on both iOS and Android
- Smooth animations and transitions
- Hardware back button supported (Android)
- Safe area handling for iPhone notch
- Keyboard handling on all input screens

---

**For more details on navigation implementation, see:**
- `NAVIGATION_UPDATE.md` - Technical details
- `START_HERE.md` - Getting started
- `README_CLI.md` - Complete documentation
