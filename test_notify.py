from pushbullet import Pushbullet

pb = Pushbullet("o.bfpqJlkU6hbOl1TRwJx0D5wYAWmeXtGJ")

push = pb.push_note("Test Title", "This is a test notification!")
print("✅ Sent!")
