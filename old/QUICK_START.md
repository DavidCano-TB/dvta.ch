# 🚀 QUICK START - Voting System

## ⚡ 3 Steps to Start Using Voting System

### Step 1: Start the Server
**Double-click:** `START_SERVER.bat`

**OR run manually:**
```bash
python main.py
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Open the Application
Open your browser and go to:
```
http://localhost:8000
```

Log in with your credentials.

### Step 3: Access Voting System
Click the **"Votaciones"** button in the navigation menu (top right on desktop, hamburger menu on mobile).

---

## ✅ That's It!

You're now in the voting system. You can:
- ➕ Create new votes
- 🗳️ Cast votes
- 📊 View results
- 🏁 Finalize votes (if you're the creator or DVD)
- 🗑️ Delete votes (if you're the creator or DVD)

---

## 🔒 Remember: Voting is Anonymous by Default

- Regular users **cannot see** who voted for what
- DVD users **can see everything**
- You can disable anonymity when creating a vote (uncheck the box)

---

## 📚 Need More Info?

- **Complete documentation:** `VOTING_SYSTEM_READY.md`
- **Spanish documentation:** `SOLUCION_VOTACIONES.md`
- **Architecture diagram:** `VOTING_ARCHITECTURE.txt`
- **Test the system:** `python test_voting_system.py`

---

## 🆘 Troubleshooting

**Problem:** Voting page won't open  
**Solution:** Make sure the server is running (Step 1)

**Problem:** Can't create vote  
**Solution:** Make sure you filled in the title and added at least 2 options

**Problem:** Can't see who voted  
**Solution:** This is normal if the vote is anonymous and you're not a DVD user

---

**Status:** ✅ READY TO USE  
**Last Updated:** May 5, 2026
