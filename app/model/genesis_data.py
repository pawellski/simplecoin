import json
GENESIS_DATA = json.loads('''{
    "header": {
        "previous_block_hash": null,
        "nonce": 2431542318
    },
    "data": [
        {
            "id": "7163c4a5-388a-4097-80ea-dc9339c7e3bc",
            "is_coinbase": true,
            "inputs": [],
            "output": {
                "new_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEovgXWjClf8AicHnAINaxRPdDuEXXosg9\nahBiwxUUi4/u6NQj2vm9hqUyTxGbReYQR5xdwaDo85VJiW0a2iNvtHLdphEIYs20\noBdaM/Qt1iNgaE60khcyILek7VICL76y\n-----END PUBLIC KEY-----\n",
                "current_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEovgXWjClf8AicHnAINaxRPdDuEXXosg9\nahBiwxUUi4/u6NQj2vm9hqUyTxGbReYQR5xdwaDo85VJiW0a2iNvtHLdphEIYs20\noBdaM/Qt1iNgaE60khcyILek7VICL76y\n-----END PUBLIC KEY-----\n",
                "new_amount": 100,
                "current_amount": 0
            },
            "fee": 0,
            "signature": "bdIPm16BUSCjzmpcCxW6EYzrOyVA56z2S0oleXHMSfiHpWHg4PQxtyW1qFKVe+HHDrIdc0KnyYkzkhwShLZzjWzUw2s6kDJlUDPixz6OK/s9AZUgvOgtRKJGun+gHd0z"
        },
        {
            "id": "bd94ab77-bf58-4a78-8fb3-8fdb23e96b67",
            "is_coinbase": true,
            "inputs": [],
            "output": {
                "new_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEEm7dqUgbhOPQzeN3fGH8nJlliKqBewXL\nnHzHM6yh6oxFX1yr26Ct745skXfSuec5OynI63h/ThaLYmSAkj9yVLWSsMWTMKtz\nqQM+0y6+uHBVvgvz6RpKVBnEGlafgQbf\n-----END PUBLIC KEY-----\n",
                "current_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEEm7dqUgbhOPQzeN3fGH8nJlliKqBewXL\nnHzHM6yh6oxFX1yr26Ct745skXfSuec5OynI63h/ThaLYmSAkj9yVLWSsMWTMKtz\nqQM+0y6+uHBVvgvz6RpKVBnEGlafgQbf\n-----END PUBLIC KEY-----\n",
                "new_amount": 100,
                "current_amount": 0
            },
            "fee": 0,
            "signature": "F9AGk+JQnsLjYrZwA1GK5ghiAzb2RrZ1OIxkxB7Kviv6dL0D7UzoFn2Sah8uAfe2igemrUIpFBs1EcXNmxV8eTKbx8rvA9tunfEiEvRIp9QTUGibJUKqlYfNpQiRhlCp"
        },
        {
            "id": "7d7cabc1-7369-4558-a1df-7f306584d17c",
            "is_coinbase": true,
            "inputs": [],
            "output": {
                "new_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAESTXMqdmWI3C0qRaXEN8s6g30XOOdj43A\nSjF59hodVwG+Ok2Ympm+oI4Pes4SktX/x7zdVLVpBT2cB8JpfrYRKEzQyUjOskXy\nrPIyZrhrLxDQtlB6m3jsYh2o18huOtPj\n-----END PUBLIC KEY-----\n",
                "current_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAESTXMqdmWI3C0qRaXEN8s6g30XOOdj43A\nSjF59hodVwG+Ok2Ympm+oI4Pes4SktX/x7zdVLVpBT2cB8JpfrYRKEzQyUjOskXy\nrPIyZrhrLxDQtlB6m3jsYh2o18huOtPj\n-----END PUBLIC KEY-----\n",
                "new_amount": 100,
                "current_amount": 0
            },
            "fee": 0,
            "signature": "YrbDJauUQgA+qcPfx08kNt3gh+fBfEXHs4evGE7AiY8sehPFLDb5qIGvhxTWj4XFseuio0WT9dN4D8TFZeyQyRtv7CmhxpdHbktGh3clyp718p1imwlnbJ1HScGEfqsP"
        },
        {
            "id": "4f146702-371f-4163-9d93-2232ad0eed5c",
            "is_coinbase": true,
            "inputs": [],
            "output": {
                "new_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEkSryFqlUzOHzH090wsn9nMTj/+TsIV0z\nU1etoPdhJhuSh7fL5P7d5wGXXBg6C7FUUPHGw582gPoKpBs0vjmk7iiBBCiW1IEm\n2SDUTJI3XsFHYWktXWgva3uz6WiewSKf\n-----END PUBLIC KEY-----\n",
                "current_owner": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEkSryFqlUzOHzH090wsn9nMTj/+TsIV0z\nU1etoPdhJhuSh7fL5P7d5wGXXBg6C7FUUPHGw582gPoKpBs0vjmk7iiBBCiW1IEm\n2SDUTJI3XsFHYWktXWgva3uz6WiewSKf\n-----END PUBLIC KEY-----\n",
                "new_amount": 100,
                "current_amount": 0
            },
            "fee": 0,
            "signature": "Sxt9+hIoznrj8+g99tKlmNpRonHNwzj6XtXZJvFQ1xYuI1vhmdAVgfH8CsqUU7+14nF66hLgfO8/VAJaS960lVQO24MEEET7roztTd6Q5WT9+ArCItZh1fiKwafFqh+X"
        }
    ]
}''', strict=False)
