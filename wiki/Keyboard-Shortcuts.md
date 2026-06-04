[Keyboard Shortcuts](Keyboard-Shortcuts)

Chat Linux Client provides comprehensive keyboard shortcuts for efficient navigation and control of all application features.

Quick Reference

 Shortcut  Action  Category 

 Ctrl+L  Clear chat history  Chat 
 Ctrl+F  Toggle search  Search 
 Ctrl+G  Find next result  Search 
 Ctrl+Shift+G  Find previous result  Search 
 Ctrl+N  New chat  Chat 
 Ctrl+S  Save chat  Chat 
 Ctrl+E  Export chat  Chat 
 Ctrl+T  Toggle timestamps  UI 
 Ctrl+M  Toggle model info  UI 
 Ctrl+H  Toggle health panel  UI 
 F12  Open health dashboard  System 
 Ctrl+P  Open settings  Settings 
 Ctrl+K  Open settings  Settings 
 Ctrl+U  Open settings  Settings 
 Ctrl+,  Open settings  Settings 
 Ctrl+R  Refresh providers  System 
 Ctrl+Shift+R  Restart application  System 
 Ctrl+Q  Quit application  System 
 F11  Toggle fullscreen  UI 
 Escape  Close search/dialog  Navigation 
 Tab  Next input field  Navigation 
 Shift+Tab  Previous input field  Navigation 
 Enter  Send message  Chat 
 Shift+Enter  New line in input  Chat 

Chat Shortcuts

Message Management
Ctrl+L - Clear chat history
Clears all messages in current conversation
Confirms with dialog to prevent accidental clearing
History is preserved in database
Ctrl+N - New chat
Creates a new conversation session
Saves current chat to history
Clears input field and context
Ctrl+S - Save chat
Manually save current conversation
Exports to JSON format
Includes metadata and timestamps
Ctrl+E - Export chat
Export conversation to various formats
Supports JSON, TXT, and Markdown
Includes full conversation history

Message Input
Enter - Send message
Sends current message to AI model
Works when focus is in input field
Triggers streaming response
Shift+Enter - New line in input
Adds line break in message input
Allows multi-line messages
Does not send message

Search Shortcuts

Search Controls
Ctrl+F - Toggle search
Opens search toolbar
Focuses on search input field
Highlights matching text in chat
Ctrl+G - Find next result
Jumps to next search match
Cycles through all matches
Wraps around to beginning
Ctrl+Shift+G - Find previous result
Jumps to previous search match
Navigates backwards through results
Wraps around to end
Escape - Close search
Closes search toolbar
Clears search highlighting
Returns focus to chat input

Search Options
Search toolbar includes options for:
Case sensitivity toggle
Whole word matching
Regular expression mode
Search scope selection

UI Shortcuts

Interface Controls
Ctrl+T - Toggle timestamps
Show/hide message timestamps
Affects display format
Persists in settings
Ctrl+M - Toggle model info
Show/hide model information panel
Displays model details and performance
Updates in real-time
Ctrl+H - Toggle health panel
Show/hide health monitoring panel
Displays provider status and metrics
Updates automatically
F11 - Toggle fullscreen
Switch between windowed and fullscreen
Maximizes chat interface
Hides system decorations

Navigation
Tab - Next input field
Navigate to next input element
Cycles through interactive elements
Wraps around to beginning
Shift+Tab - Previous input field
Navigate to previous input element
Moves backwards through elements
Wraps around to end

Settings Shortcuts

Settings Access
Multiple shortcuts for opening settings:
Ctrl+P - Open settings
Ctrl+K - Open settings
Ctrl+U - Open settings
Ctrl+, - Open settings

Settings Navigation
Once in settings dialog:
Tab - Navigate between settings sections
Enter - Activate selected option
Escape - Close settings dialog
Ctrl+S - Save and apply settings

System Shortcuts

System Operations
F12 - Open health dashboard
Opens comprehensive health monitoring
Shows system status and metrics
Provides remediation options
Ctrl+R - Refresh providers
Refresh provider connectivity
Update model availability
Recheck provider status
Ctrl+Shift+R - Restart application
Restart Chat Linux Client
Preserves current session
Reloads configuration
Ctrl+Q - Quit application
Exit Chat Linux Client
Saves current state
Clean shutdown

Diagnostics
F12 also provides access to:
System diagnostics
Performance metrics
Error logs
Remediation tools

Advanced Shortcuts

Context-Sensitive Shortcuts
Some shortcuts work differently based on context:

In Search Mode
Enter - Find next result
Shift+Enter - Find previous result
Escape - Exit search mode

In Settings Dialog
Ctrl+Tab - Next settings tab
Ctrl+Shift+Tab - Previous settings tab
Enter - Apply selected setting

In Model Selection
Arrow Keys - Navigate model list
Enter - Select model
Escape - Close model dropdown

Modifier Combinations
Ctrl+Alt+T - Toggle theme (dark/light)
Ctrl+Alt+S - Screenshot interface
Ctrl+Alt+D - Debug mode toggle
Ctrl+Alt+P - Performance panel

Customization

Shortcut Configuration
Shortcuts can be customized in settings:
Open settings (Ctrl+P)
Navigate to "Keyboard" section
Modify shortcut assignments
Apply and save changes

Shortcut Conflicts
System checks for conflicts:
Warns about duplicate shortcuts
Suggests alternative combinations
Validates shortcut availability
Preserves default shortcuts

Implementation Details

Shortcut Handling

Event Processing
Event Capture: Keyboard events captured at window level
Context Detection: Current context determines action
Priority Handling: System shortcuts have priority
Conflict Resolution: User preferences override defaults

Shortcut Storage

Troubleshooting Shortcuts

Common Issues

Shortcuts Not Working

Search Shortcuts

Settings Shortcuts

Debug Mode

Accessibility

Alternative Input Methods
For users who have difficulty with keyboard shortcuts:
Mouse Navigation: All features accessible via mouse
Menu Access: All shortcuts available in menus
Toolbar Buttons: Common functions in toolbar
Context Menu: Right-click options available

Accessibility Features
Visual Indicators: Shortcuts shown in menus
Keyboard Navigation: Full keyboard accessibility
Screen Reader Support: Compatible with screen readers
High Contrast: Works with high contrast themes

Performance Considerations

Shortcut Performance
Event Handling: Optimized for minimal latency
Memory Usage: Efficient shortcut storage
CPU Impact: Minimal impact on performance
Response Time: Instant response to shortcuts

Best Practices
Use frequently needed shortcuts
Customize for workflow efficiency
Learn essential shortcuts first
Practice muscle memory

Learning Resources

Shortcut Learning
Essential Shortcuts: Start with Ctrl+F, Ctrl+L, F12
Daily Use: Incorporate shortcuts into routine
Reference Guide: Keep shortcut list handy
Practice: Use shortcuts regularly

Teaching Tips
Group by Category: Learn related shortcuts together
Mnemonic Devices: Use memory aids for shortcuts
Visual Cues: Look for menu indicators
Progressive Learning: Add new shortcuts gradually

Future Enhancements

Planned Improvements
Custom Shortcuts: User-defined shortcut combinations
Macro Support: Record and playback action sequences
Gesture Support: Mouse gesture shortcuts
Voice Commands: Voice-activated shortcuts
Context Awareness: Smart shortcut suggestions

Development Roadmap
Q3 2026: Custom shortcut editor
Q4 2026: Macro recording system
Q1 2027: Gesture recognition
Q2 2027: Voice command integration

Related Documentation
[Enhanced Features](Enhanced-Features)
[Search Functionality](Search-Functionality)
Health Monitoring
Settings
[Troubleshooting](Troubleshooting)

Keyboard shortcuts provide efficient access to all Chat Linux Client features, enabling power users to navigate and control the application with maximum efficiency.