# Projeto1SegApli

Santiago Benites fc54392

Project done with python

# TODO

- Setup files
- Add utility to .user files, sending them to server for verification and adding random bytes to use as PIN
- Add utility to .auth file, leading to symmetric cryptography between bank and client, and asymmetric between client and store
- Add more needed verifications like time part of message
- Implement attacks to defend
- Add threads to deal with 2 clients at the same time
- Vcc file in user
- User file passes to private key
- Add authentication between user and bank
- Add symmetric key between bank and user for encripton

# Git commands

## Starting the repo
```
echo "# Projeto1SegApli" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:SantigBenites/Projeto1SegApli.git
git push -u origin main
```

## Commiting to repo

```
git pull origin main (carefull with pulling over non commited work)
git add -A
git commit -m "message"
git push origin main
```
