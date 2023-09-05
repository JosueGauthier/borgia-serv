# Get started

## Creating a user

The administrator account should not be used during production. It simply allows you to create a new real user and give them the right permissions.

- Therefore, log in with the user name `admin` and the password **ADMIN_PASSWORD** defined above during configuration.

> **The software is for the moment not yet fully translated. Some tabs/buttons may still be in French**

- Go to the presidents group by clicking on `Groups / Presidents` in the side menu.

- Go to `Users / New` in the side menu to create a new user and fill out the form. The user present will be designated president, it is therefore necessary to create the real account of the president of the association.

- Click on `Group management / President management` and add the newly created account.

- The new account can now connect and have access to the presidents group. It can disable the `admin` account in the user list. Likewise, it can add other users and add them to the right groups.

## Creating a store

All stores must now be created. Only one example will be detailed, but the same goes for the others.

- Click on `Store / New` from the presidents' group interface and fill out the form.

- By default, no one is manager or associate of the new store. It is therefore necessary to add users to these groups (at least to the store managers group). The leaders will then be able to manage the associates themselves.

## Usage settings

### Miscellaneous

While in the presidents group, go to the settings system and modify all the information that seems useful to you.

### Lydia

The two public and private keys `LYDIA_API_TOKEN` & `LYDIA_VENDOR_TOKEN` allow the account to be identified with Lydia. This information is obtained by contacting Lydia support directly after opening a professional account with them.

### Viva Wallet 

TODO

## TODO: CHECK HERE IN 5.1+

Likewise, you must change the two urls `LYDIA_CALLBACK_URL` and `LYDIA_CONFIRM_URL` by modifying the first part which only concerns the domain (`borgia.iresam.org` for example). Please note, `LYDIA_CONFIRM_URL` must be in `http` and Borgia will automatically do the redirection if SSL is activated, but `LYDIA_CALLBACK_URL` **MUST** be in `https` if SSL is activated!