# Shadow Roll Discord Bot

## Overview

Shadow Roll is a Discord bot that provides a gacha-style character collection game inspired by "The Eminence in Shadow" anime. Players can summon anime characters, build collections, and compete on leaderboards using a dark, futuristic theme with French interface. The bot implements a single-message interaction system where all navigation happens through Discord button interactions without generating new messages.

## System Architecture

### Backend Architecture
- **Framework**: Discord.py (Python 3.11)
- **Database**: SQLite with aiosqlite for async operations
- **Architecture Pattern**: Modular component-based system with centralized core
- **Navigation System**: Button-based menu system that edits existing messages for seamless UX

### Frontend Architecture
- **Interface**: Discord embeds with rich formatting and button navigation
- **Theme**: Dark futuristic design inspired by "The Eminence in Shadow"
- **Navigation**: Button-based menu system that edits existing messages
- **Visual Design**: ANSI color codes, styled separators, and consistent French branding
- **Language**: Complete French interface with "ɪ ᴀᴍ ᴀᴛᴏᴍɪᴄ" branding

## Project Structure (Reorganized v2.0)

### Core Components (`core/`)
1. **bot.py** - Main ShadowRollBot class with centralized event handling and setup
2. **config.py** - Centralized configuration management with French messages
3. **database.py** - Comprehensive SQLite database manager with proper async operations
4. **models.py** - Data models for Character, Player, Achievement, etc.

### Modular System (`modules/`)
1. **admin.py** - Secure administrative commands (givecoins, createchar, banuser, etc.)
2. **menu.py** - Complete button-based navigation system with all views
3. **commands.py** - Slash command implementations (/menu, /roll, /profile, /daily)
4. **achievements.py** - Achievement tracking and reward system
5. **utils.py** - Utility functions including **FIXED** get_display_name() for "User: Unknown" bug

### Key Fixes & Improvements
- **FIXED "User: Unknown" Bug**: Centralized username handling in utils.get_display_name()
- **Removed Code Duplication**: Eliminated redundant menu systems and commands
- **Centralized Admin Commands**: All admin functionality in single secure module
- **Modular Architecture**: Clean separation of concerns with well-defined modules
- **French Interface**: Complete translation with Shadow theme consistency

## Game Systems

1. **Character System** - 40+ anime characters with rarity, value, and images
2. **Economy System** - Shadow Coins currency with costs and rewards
3. **Achievement System** - Progress tracking and milestone rewards with coin bonuses
4. **Cooldown System** - Rate limiting for rolls and interactions
5. **Rarity System** - Weighted probability system (Common 60% → Duo 0.1%)
6. **Ban System** - User management with ban/unban functionality

## Data Flow

### User Interaction Flow
1. User invokes `!menu` or `/menu` command
2. Bot creates interactive embed with Discord buttons
3. User clicks button to navigate to subsection (Profile, Roll, Collection, etc.)
4. Bot edits existing message with new content and appropriate view
5. User can navigate seamlessly using buttons
6. All interactions happen within single message thread

### Character Summoning Flow
1. User clicks "🎲 Invocation" button
2. System checks ban status, cooldown, and currency requirements
3. Random character selected based on rarity weights
4. Character added to user inventory with database transaction
5. Results displayed with character details, image, and rarity styling
6. Achievement system automatically checks and awards progress milestones
7. User can roll again or return to main menu

### Database Operations
- **Player Management**: Create/update player profiles with proper username syncing
- **Inventory System**: Track character ownership with counts and metadata
- **Character Storage**: Master character database with 40+ pre-populated characters
- **Achievement Tracking**: Automatic progress monitoring and reward distribution

## External Dependencies

### Required Packages
- `discord.py>=2.5.2` - Discord API wrapper
- `aiosqlite>=0.21.0` - Async SQLite database operations

### External Services
- **Discord API** - Bot authentication and message handling
- **Image Hosting** - Character images (URLs stored in database)
- **Anime Character Data** - Pre-populated with characters from Naruto, One Piece, Dragon Ball Z, Attack on Titan

### Configuration Requirements
- `DISCORD_TOKEN` environment variable for bot authentication
- Admin user IDs configured in BotConfig.ADMIN_IDS
- Database file path configuration

## Deployment Strategy

### Development Environment
- **Platform**: Replit with Python 3.11
- **Startup**: Automated pip installation and bot execution via main.py
- **Database**: Local SQLite file (`shadow_roll.db`)
- **Logging**: File and console logging with configurable levels

### Production Considerations
- Environment variable management for sensitive tokens
- Database backup and migration strategies
- Comprehensive error handling and recovery mechanisms
- Rate limiting compliance with Discord API
- Modular architecture allows easy feature additions

### Monitoring and Maintenance
- Centralized logging system with different log levels
- Error tracking and debugging capabilities
- Performance monitoring for database operations
- Clean modular code structure for easy maintenance

## Recent Changes

- **June 28, 2025**: Complete Character Persistence System (v5.2.0)
  - **📁 PERSISTENT CHARACTER STORAGE**: All admin-created characters now automatically saved to permanent JSON storage
  - **🔄 DUAL STORAGE SYSTEM**: Characters stored in both SQLite database and persistent JSON file
  - **🛡️ GUARANTEED PERSISTENCE**: No character loss during bot restarts or updates
  - **⚡ NEW ADMIN COMMANDS**: !createcharpersistent, !syncchars, !charstats, !backupchars, !findchar
  - **📊 ADVANCED STATISTICS**: Detailed character analytics with rarity and anime breakdowns
  - **💾 AUTOMATIC BACKUPS**: Timestamped backups created automatically with manual backup support
  - **🔧 SEAMLESS INTEGRATION**: Works with existing admin interface and preserves all player inventories
  - **📈 161 CHARACTERS SYNCHRONIZED**: All existing characters migrated to persistent storage

- **June 26, 2025**: Complete Series Database Fix (v5.1.3)
  - **📊 SERIES DATABASE REPAIR**: Fixed missing anime series in database - created all 22 series automatically
  - **🎯 BLUE LOCK RESTORED**: Blue Lock now appears correctly with all other series in admin interface
  - **⚖️ BALANCED BONUSES**: Applied size-based bonus system (large series +1.5%, medium +2.0%, small +2.5%)
  - **🔧 AUTO-CREATION SYSTEM**: Fixed automatic series creation to prevent future missing series
  - **✅ COMPLETE COVERAGE**: All 22 anime now have proper series entries with balanced bonuses

- **June 26, 2025**: Admin Series Management Fix (v5.1.2)  
  - **🔧 FIXED MISSING BUTTONS**: Resolved admin series interface showing text without interactive buttons
  - **❌ REMOVED DUPLICATE CLASS**: Eliminated conflicting SeriesManagementView class from admin_new.py
  - **✅ PROPER SERIES INTERFACE**: Admin series management now uses complete interface with all buttons
  - **🎖️ FULL FUNCTIONALITY**: Series creation, assignment, modification, and deletion buttons working
  - **🛠️ CLEAN ADMIN SYSTEM**: Resolved conflicts between different admin module implementations

- **June 26, 2025**: Database Cleanup & Duplicate Removal (v5.1.1)
  - **🧹 COMPLETE DATABASE CLEANUP**: Removed all duplicate character definitions from database.py
  - **🔧 FIXED CUSTOM CHARACTERS SECTION**: Eliminated the custom_characters section that was causing duplicates
  - **📊 CLEAN CHARACTER SYNC**: All 169 characters now unique and properly organized by anime series
  - **✅ ADMIN-ONLY CHARACTER MANAGEMENT**: Characters now managed exclusively through admin commands
  - **🏗️ IMPROVED ARCHITECTURE**: Cleaner code structure with no redundant character definitions
  - **🚀 STABLE STARTUP**: Bot now starts reliably without database conflicts

- **June 26, 2025**: Complete Evolve Craft System (v5.1.0)
  - **🔮 RARITY EVOLVE**: New ultra-rare Evolve rarity between Mythical and Titan (purple theme)
  - **⚡ AUTO-CRAFT SYSTEM**: All Evolve characters automatically generate craft recipes (10 base → 1 Evolve)
  - **🛠️ SMART DETECTION**: System automatically detects base characters for recipe creation
  - **👨‍💻 ADMIN COMMANDS**: !createevolve command for easy Evolve character creation
  - **🎯 DIO EVOLVE**: First Evolve character created (150K SC value, craftable from 10 DIO)
  - **🔧 EQUIPMENT BUG FIX**: Sold characters automatically removed from equipment slots
  - **📱 FULL INTEGRATION**: Craft button in main menu, complete UI system, /craft command

- **June 26, 2025**: Admin Character Persistence System (v5.0.0)
  - **🔄 AUTO-SYNC TO CODE**: All admin-created characters now automatically sync to database.py
  - **📁 PERSISTENT STORAGE**: Characters created with !createchar are saved in both database and code
  - **🎖️ AUTO-SERIES CREATION**: Series are automatically created when new anime are added via admin commands
  - **🔧 MANUAL SYNC**: Added !syncchars command to manually sync all characters to code
  - **🏈 BLUE LOCK FIX**: Added !fixbluelock command to restore missing Blue Lock characters and series
  - **📊 COMPREHENSIVE SYSTEM**: Complete solution for admin character management and persistence
  - **🛠️ ADMIN SYNC MODULE**: New admin_character_sync.py module handles all synchronization operations

- **June 25, 2025**: Button Selection & Auto-Series System (v4.9.2)
  - **🔘 BUTTON SELECTION**: Both !addimage and !lookcard now show interactive buttons when multiple characters found
  - **🎯 ONE-CLICK SELECTION**: No more typing exact names - just click the button for the character you want
  - **🆕 AUTO-SERIES CREATION**: New anime automatically get series entries with balanced bonuses when characters are added
  - **📊 SMART BONUSES**: Popular anime get lower bonuses (1.5% coin, 0.3% rarity) vs smaller series (2.0% coin, 0.5% rarity)
  - **🔄 INSTANT SYNC**: Series are created automatically during character synchronization
  - **⏰ DYNAMIC COOLDOWN**: Ultra-rare pulls (Mythical, Titan, Duo, Secret) have 2-second cooldown vs 0.5s for normal rarities

- **June 25, 2025**: Custom Character Management System (v4.9.0)
  - **📝 CODE-BASED CHARACTERS**: All custom characters now defined directly in core/database.py
  - **✏️ EASY EDITING**: Dedicated section for user's custom characters with clear formatting
  - **🔧 INSTANT SYNC**: Characters automatically sync when code is modified
  - **📚 COMPREHENSIVE GUIDE**: Created PERSONNAGES_GUIDE.md with detailed instructions
  - **🎯 ORGANIZED STRUCTURE**: Separated base characters from custom characters
  - **⚡ REAL-TIME UPDATES**: Bot restarts automatically apply character changes
  - **🛠️ FULL CONTROL**: User can modify names, rarities, values, and images directly in code

- **June 25, 2025**: Coin Bonus System Complete Fix (v4.8.2)
  - **🐛 BONUS CALCULATION FIXED**: Corrected series coin bonus display (removed +1390% bug)
  - **🪙 FULL IMPLEMENTATION**: Series coin bonuses now properly apply to all game systems
  - **📊 ACCURATE DISPLAY**: Bonus percentages now show correct values in all interfaces
  - **🎁 DAILY REWARDS**: Series bonuses correctly applied to daily rewards
  - **🪙 CHARACTER SALES**: Series bonuses correctly applied to character sale profits with real-time display
  - **🏆 ACHIEVEMENTS**: Series bonuses correctly applied to achievement rewards
  - **⚔️ EQUIPMENT INTEGRATION**: Equipment and series bonuses now stack properly
  - **🛒 SELL INTERFACE**: Enhanced sell system shows actual prices with bonuses applied
  - **💎 BONUS PREVIEW**: Confirmation screens show base price vs final price with bonus percentage
  - **🔧 COMPREHENSIVE FIX**: All coin bonus systems now functional across the bot

- **June 25, 2025**: Admin Series Management System (v4.8.0)
  - **🎖️ SERIE MANAGEMENT**: Complete admin interface for managing anime series
  - **🆕 CREATE SERIES**: Create new anime series with custom bonus configurations
  - **📝 ASSIGN CHARACTERS**: Assign characters to series with intuitive interface
  - **⚙️ MODIFY SERIES**: Rename series, edit bonus values, reorganize collections
  - **📋 DETAILED VIEW**: View complete series information with character breakdown
  - **🗑️ SAFE DELETION**: Remove series with confirmation safeguards
  - **💻 LEGACY COMMANDS**: Fast text commands for experienced admins (!createseries, !assign, etc.)
  - **🔧 DUAL INTERFACE**: Modern GUI + legacy command system for all preferences
  - **🎯 INTEGRATION**: Seamlessly integrated with existing admin panel and menu

- **June 25, 2025**: Enhanced Guide System (v4.7.0)
  - **📖 COMPREHENSIVE GUIDE**: Complete 4-page guide system with all new features
  - **🎯 PAGE NAVIGATION**: Smooth navigation with previous/next and direct page buttons
  - **⚡ ALL SYSTEMS COVERED**: Equipment, series bonuses, marketplace, potions explained
  - **🪙 STRATEGY SECTION**: Advanced tips and hidden features for experienced players
  - **📱 MODERN LAYOUT**: Clean organization with detailed explanations and examples
  - **🔥 REAL-TIME INFO**: Shows current version numbers and accurate statistics
  - **🎖️ COMPLETE COVERAGE**: All 151 characters, 21 series, 8 rarities documented

- **June 25, 2025**: Complete Equipment & UI System (v4.6.3)
  - **🎯 TWO-COLUMN LAYOUT**: Invocation display reorganized with character info left, bonuses right
  - **📱 IMPROVED READABILITY**: Compact bonus format for cleaner presentation
  - **🏠 MENU NAVIGATION FIXED**: All navigation returns to proper detailed menu format
  - **⚔️ EQUIPMENT BONUSES WORKING**: Rarity and coin bonuses actually apply to gameplay
  - **📊 COMPLETE BREAKDOWN**: Shows Equipment/Series/Potions/Total with exact percentages
  - **🪙 COIN BONUSES APPLIED**: Equipment bonuses work on daily rewards and character sales
  - **🎲 RARITY BONUSES APPLIED**: Equipment bonuses actually increase rare character chances
  - **🔥 REAL-TIME FEEDBACK**: Players see exactly what bonuses are active and their values

- **June 25, 2025**: Menu Navigation Fix (v4.6.1)
  - **🏠 MENU CONSISTENCY**: Fixed navigation from patch notes and equipment sections
  - **UNIFIED FORMAT**: All "back to menu" buttons now use consistent Shadow Roll formatting
  - **DISPLAY CORRECTION**: Main menu now properly shows "ɪ ᴀᴍ ᴀᴛᴏᴍɪᴄ" branding and clean layout
  - **NAVIGATION STABILITY**: Eliminated conflicting menu creation functions
  - **USER EXPERIENCE**: Seamless navigation maintains proper theme across all sections

- **June 25, 2025**: Ultra-Rare Equipment System (v4.6.0)
  - **⚔️ EQUIPMENT SYSTEM**: Ultra-rare characters (Titan/Duo/Secret) can be equipped for global bonuses
  - **3 EQUIPMENT SLOTS**: Maximum 3 characters can be equipped simultaneously
  - **PASSIVE BONUSES**: Titan (+2% rarity), Duo (+5% coins), Secret (+3% both)
  - **GLOBAL EFFECTS**: Bonuses apply to all game systems (summons, rewards, sales)
  - **COMPLETE INTEGRATION**: Equipment bonuses stack with existing series bonuses
  - **MENU INTEGRATION**: New ⚔️ Equipment button and /equipment slash command
  - **PROFILE DISPLAY**: Shows equipped characters and active bonuses in profile
  - **STRATEGIC DEPTH**: Collecting ultra-rares now provides permanent gameplay benefits

- **June 25, 2025**: Shop Rebalance & Navigation Fix (v4.5.1)
  - **🛒 SHOP REBALANCED x10**: All shop prices increased 10x to prevent potion abuse
  - **ECONOMY PROTECTION**: Legendary Elixir 1,800→18,000 SC, Mythical Serum 4,000→40,000 SC
  - **PATCH NOTES NAV FIXED**: Corrected menu navigation from patch notes back to main menu
  - **STANDALONE FUNCTION**: Created centralized create_main_menu_embed() function
  - **SMOOTH UX**: Proper Shadow theme consistency across all navigation

- **June 25, 2025**: Patch Notes System Implementation (v4.5.0)
  - **📜 PATCH NOTES BUTTON**: Added permanent patch notes button to main menu
  - **COMPREHENSIVE HISTORY**: Complete version history from v2.0.0 to current in French
  - **SLASH COMMAND**: Added /patchnotes command for direct access
  - **PAGINATED NAVIGATION**: Navigate through versions with previous/next buttons
  - **SHADOW THEME**: Consistent dark theme formatting with Discord embeds
  - **MARKDOWN INTEGRATION**: Automated loading from PATCH_NOTES.md file
  - **REFRESH FUNCTIONALITY**: Real-time updates without bot restart
  - **USER CLARITY**: Clear historical overview of all non-admin features and improvements

- **June 23, 2025**: Real Functional Bonuses Implementation (v4.4.0)
  - **ALL BONUSES NOW REAL**: Series bonuses actually affect gameplay, not just cosmetic display
  - **COIN BONUSES FUNCTIONAL**: Applied to daily rewards, achievement rewards, and character sales
  - **RARITY BONUSES FUNCTIONAL**: Increase actual chances of rare characters in summons
  - **COMPLETE IMPLEMENTATION**: Bonuses work in all game systems with proper calculations
  - **SERIES BONUSES VISIBLE**: Fixed display of series bonuses in roll invocations (🎖️ icons)
  - **AUTOMATIC SET COMPLETION**: Sets automatically detected and marked complete when all characters owned
  - **ALL ANIME SERIES ADDED**: 21 complete series sets with balanced bonus system
  - **COMPREHENSIVE COVERAGE**: Every anime from database now has its own character set
  - **BALANCED BONUSES**: Bonus strength scales with series size (Naruto +2.5% vs small series +0.5%)
  - **STRATEGIC GAMEPLAY**: Large series offer better rewards but require more collection effort
  - **ULTRA-RARE DISPLAY FIXED**: Secret and Duo rarities now properly visible in inventory and collection
  - **CORRECT SORTING**: Fixed database queries to show proper rarity hierarchy (Secret → Duo → Titan → etc.)
  - **DUAL ADMIN SYSTEM**: Modern GUI interface + comprehensive legacy commands
  - **ALL COMMANDS WORKING**: 25+ admin commands with proper error handling and validation

- **June 23, 2025**: Admin Command Bug Fix (v3.0.1)
  - **LOOKCARD FIX**: Fixed !lookcard command displaying duplicate error messages
  - **ERROR CLARITY**: Distinguished between lookcard and addimage command error messages
  - **CLEAN DISPLAY**: Command now shows character cards without conflicting messages
  - **SYSTEM STABLE**: All 151 characters accessible via admin preview command

- **June 23, 2025**: Potion System Rebalanced & Secret Rarity Added (v3.0.0)
  - **POTION REBALANCE**: Potions now only affect Common to Mythical rarities (excluded Titan, Duo, Secret)
  - **ULTRA-RARE PROTECTION**: Titan, Duo, and Secret rarities immune to potion effects for fair gameplay
  - **SERIES BONUSES REMAIN**: Collection set bonuses still affect all rarities including ultra-rares
  - **NEW SECRET RARITY**: Added 🌑 Secret rarity at 0.001% chance - the rarest tier
  - **AKANE KUROKAWA**: First Secret character from Oshi no Ko (150,000 Shadow Coins)
  - **DRAMATIC ANIMATION**: Custom 3-stage summoning animation with void/darkness theme
  - **8 RARITY SYSTEM**: Complete balanced system from Common to Secret

- **June 23, 2025**: Character Sets System (v2.9.0)
  - **NEW SETS SYSTEM**: Complete collection sets with passive bonuses
  - **AKATSUKI SET**: Naruto characters with +1% global rarity bonus
  - **STRAW HAT PIRATES**: One Piece characters with +15% coin bonus
  - **AUTOMATIC DETECTION**: System checks collection completion automatically
  - **PASSIVE BONUSES**: Permanent benefits for completing entire series
  - **SERIES BUTTON**: New 🎖️ Séries button in main menu
  - **PROGRESS TRACKING**: Visual progress bars and completion status

- **June 23, 2025**: Enhanced Index System (v2.8.0)
  - **INDEX UPGRADE**: Transformed basic index into complete collection tracker
  - **OWNERSHIP STATUS**: Shows ✅ Possédé / ❌ Non possédé for every character with counts
  - **SERIES STATISTICS**: New stats view showing completion percentage by anime series
  - **PROGRESS TRACKING**: Visual progress bars and completion tiers (COMPLÈTE, AVANCÉE, etc.)
  - **ADVANCED FILTERING**: Filter by anime series, rarity, or search by name
  - **DUAL VIEWS**: Toggle between character list and series statistics
  - **SATISFYING COMPLETION**: True collection tracking experience for collectors

- **June 23, 2025**: Mission System Removed (v2.7.6)
  - **REMOVED MISSION FUNCTIONALITY**: Completely removed missions system per user request
  - **CLEANED MENU**: Removed mission button from main navigation
  - **DATABASE CLEANUP**: Removed active_missions table and references
  - **SIMPLIFIED UI**: Cleaner main menu without mission functionality

- **June 22, 2025**: Achievements System Simplified (v2.7.5)
  - **SIMPLIFIED INTERFACE**: Restored clear, simple achievements display
  - **REMOVED COMPLEXITY**: No more confusing categories and progress bars
  - **CLEAR STATUS**: Simple ✅ COMPLÉTÉ / ❌ À DÉBLOQUER / ⏳ progress format
  - **BETTER NAVIGATION**: Simple previous/next page buttons
  - **USER FRIENDLY**: Much easier to understand achievement progress

- **June 22, 2025**: Admin Card Preview Command Added (v2.7.4)
  - **NEW ADMIN COMMAND**: Added !lookcard command for character preview
  - **CARD DISPLAY**: Shows character like in summons with rarity styling
  - **SMART SEARCH**: Partial name matching with multiple results handling
  - **ADMIN TOOL**: Useful for checking character appearance and stats

- **June 22, 2025**: Ultra-Rare Rarities Re-enabled (v2.7.3)
  - **TITAN & DUO RESTORED**: Re-activated ultra-rare tiers per user request
  - **7 RARITIES ACTIVE**: Full system with Common to Duo (0.1% ultimate rarity)
  - **EXISTING TITANS**: 3 Titan characters found in database
  - **SYSTEM UPDATED**: All interfaces show complete 7-tier rarity hierarchy

- **June 22, 2025**: Bot Startup Fix & Complete System Finalization (v2.7.1)
  - **STARTUP FIXED**: Resolved Discord rate limiting issue by disabling auto-sync of slash commands
  - **ADMIN SYNC COMMAND**: Added !synccommands for manual slash command synchronization
  - **BOT OPERATIONAL**: Successfully connects to Discord and 2 guilds
  - **SYSTEM COMPLETE**: All 7 rarity tiers operational with 124 total characters
  - **ZERO DUPLICATES**: Database fully cleaned and optimized

- **June 22, 2025**: Complete System Overhaul (v2.7)
  - **DATABASE CLEANUP**: Removed all character duplicates (Zoro, Joseph, Shadow)
  - **TITAN FINALIZED**: 3 characters - Zoro (50K), Shadow (65K), Joseph µ (60K)
  - **DUO CONFIRMED**: 1 character - DIO VS JOJO (100K)
  - **SYSTEM INTEGRATION**: All displays, achievements, and mechanics updated
  - **GUIDE SYSTEM**: New interactive guide with complete rarity documentation
  - **FINAL STATISTICS**: 124 total characters across 7 rarity tiers

- **June 22, 2025**: New Ultra-Rare Rarities Added (v2.6)
  - **NEW TITAN RARITY**: Added 🔱 Titan (0.3% chance) - more rare than Mythical
  - **NEW DUO RARITY**: Added ⭐ Duo (0.1% chance) - the ultimate rarity
  - **TITAN CHARACTERS**: Zoro (One Piece), Shadow (Eminence in Shadow), Joseph µ (JoJo)
  - **DUO CHARACTER**: DIO VS JOJO (100,000 Shadow Coins value)
  - **UPDATED SYSTEMS**: All potion effects, inventory display, and rarity calculations now support new rarities
  - **COMPLETE INTEGRATION**: New rarities work with all existing game mechanics

- **June 22, 2025**: Effects & Image System Fixes (v2.5.1)
  - **FIXED POTION EFFECTS**: Changed from additive to multiplicative bonuses for realistic scaling
  - **TIME DISPLAY**: Added remaining time display for all active potion effects
  - **IMAGE SELECTION**: Fixed addimage command - now shows selection menu when multiple characters share names
  - **IMPROVED UX**: Better visual feedback for effect durations and character selection

- **June 18, 2025**: Complete bot reorganization and refactoring (v2.0)
  - **MAJOR REORGANIZATION**: Restructured entire codebase into clean modular architecture
  - **REMOVED REDUNDANCIES**: Eliminated duplicate menu systems, commands, and utility functions
  - **FIXED "User: Unknown" BUG**: Centralized username management with proper fallbacks
  - **CENTRALIZED ADMIN COMMANDS**: All admin functionality in single secure module
  - **CLEAN FILE STRUCTURE**: Organized into core/ and modules/ directories
  - **REMOVED OBSOLETE FILES**: Deleted old redundant implementations
  - **IMPROVED MAINTAINABILITY**: Clear separation of concerns and well-documented code
  - **COMPLETE FRENCH INTERFACE**: Maintained Shadow theme with proper translations
  - **ENHANCED SECURITY**: Consolidated admin permissions and validation

## File Structure Summary

### Removed (Redundant/Obsolete)
- `bot.py`, `commands.py`, `enhanced_menu.py`, `menu_system.py`, `shadow_menu.py`
- `shadow_roll_bot.py`, `shadow_roll_main.py`, `trade_system.py`
- `achievements.py`, `utils.py`, `admin_commands.py`, `models.py`, `database.py`, `config.py` (root level)
- `database/` directory and all `__pycache__` directories

### New Clean Structure
```
├── main.py                    # Clean entry point
├── core/                      # Core components
│   ├── bot.py                # Main bot class
│   ├── config.py             # Configuration
│   ├── database.py           # Database manager
│   └── models.py             # Data models
├── modules/                   # Functional modules
│   ├── admin.py              # Admin commands
│   ├── menu.py               # Navigation system
│   ├── commands.py           # Slash commands
│   ├── achievements.py       # Achievement system
│   └── utils.py              # Utilities (fixes username bug)
└── README.md                 # Documentation
```

## Changelog

- **June 22, 2025**: Interactive Image Management System (v2.5)
  - INTERACTIVE INTERFACE: Created shop-like interface for image management with !suggest command
  - ONE-AT-A-TIME WORKFLOW: Shows one character at a time with buttons for navigation
  - MODAL INPUT: Click "Ajouter Image" button opens modal for URL input
  - SMART NAVIGATION: "Passer" to skip, "Arrêter" to stop session anytime
  - AUTO-PROGRESSION: Automatically moves to next character after successful image addition
  - PERSISTENT STORAGE: Fixed automatic image overwriting - custom images now saved permanently
  - NUMERIC SELECTION: Alternative !addimage system with number selection from search results
  - URL VALIDATION: Automatic validation of image accessibility and content type

- **June 22, 2025**: Achievements System Overhaul (v2.3)
  - FIXED ACHIEVEMENT DISPLAY: Completely reorganized achievement menu with consistent progress bars
  - AUTO-AWARD SYSTEM: Implemented automatic achievement granting for completed objectives
  - CLEAR STATUS INDICATORS: Distinguished between "SUCCÈS OBTENU" and "EN COURS" with proper formatting
  - REWARD CLARITY: Fixed reward display showing correct status based on achievement completion
  - PROGRESS ACCURACY: Corrected calculation and display of achievement progress across all categories
  - RETROACTIVE AWARDS: 11 previously earned achievements automatically granted to eligible players

- **June 21, 2025**: Advanced Image Search System (v2.2)
  - NEW IMAGE FINDER: Created automatic high-quality image search system
  - API INTEGRATION: Integrated AniList and Jikan (MyAnimeList) APIs for authentic character images
  - ADMIN COMMANDS: Added !searchimage and !findimages commands for image management
  - QUALITY VALIDATION: Automatic image quality and accessibility verification
  - RATE LIMITING: Smart delays to respect API limits and avoid blocking
  - REPLACED OLD SYSTEM: Removed non-functional web scraping with reliable API-based solution

- **June 18, 2025**: Display fixes and Index system addition (v2.1)
  - Fixed ANSI display issue: Removed all ANSI color codes causing raw code display in Discord
  - Added Index system: New 📚 Index feature displaying all available characters in the game
  - New slash command: Added /index command for direct access to character index  
  - Enhanced navigation: Updated main menu to include Index option with clean pagination
  - Database extensions: Added get_all_characters() and get_total_characters_count() methods
  - Improved UX: Clean Discord formatting with proper embeds instead of terminal codes
  - Performance optimized: Efficient pagination system for fast character browsing

- **June 18, 2025**: Complete reorganization and refactoring (v2.0)
  - Removed all redundant and obsolete code
  - Fixed "User: Unknown" bug with centralized username handling
  - Created clean modular architecture
  - Centralized admin commands with security
  - Maintained complete French Shadow theme
  - Enhanced maintainability and removed code duplication

## User Preferences

Preferred communication style: Simple, everyday language.