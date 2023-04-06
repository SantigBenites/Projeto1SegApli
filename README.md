# Projeto1SegApli

Santiago Benites fc54392

Project done with python

# TODO

- Setup files
- Add more needed verifications like time part of message
- Vcc file in user
- Add IP:Port of bank to Vcc file
- Cipher amount account of vcc file, with bank public key
- Client sign content of vcc file when it receives it
- Make sure client is always active and can accept multiple operations
- Add authentication between user and bank
- Use different IVs for encrypton
- Make sure the project can be compiled from zero in a VM 
- Hashes em algum lado

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
