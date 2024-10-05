import DBHelper from '../../helpers/DBHelper.js';
import RiotHelper from '../../helpers/RiotHelper.js';
import axiosRetry from 'axios-retry';
import axios from 'axios';
import { logger } from '../../config/logging.js';
import { SummonerDTO } from '../../interfaces/CustomInterfaces.js';

export default class FillSummonersTask {
  dbHelper: DBHelper;
  riotHelper: RiotHelper;
  accountNames: { name: string; tag: string; core: boolean }[];

  constructor(accountNames?: { name: string; tag: string; core: boolean }[]) {
    this.dbHelper = DBHelper.getInstance();
    this.riotHelper = RiotHelper.getInstance();
    axiosRetry(axios, {
      retries: 4, // number of retries
      retryDelay: (retryCount) => {
        logger.warn(`retry attempt: ${retryCount}`);
        return retryCount * 2000; // time interval between retries
      },
    });

    if (accountNames) {
      this.accountNames = accountNames;
    } else {
      this.accountNames = [
        {
          name: 'AngryBacteria',
          tag: 'cnap',
          core: true,
        },
        {
          name: 'BriBri',
          tag: '0699',
          core: true,
        },
        {
          name: 'VerniHD',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'Baywack',
          tag: 'CnAP',
          core: true,
        },
        {
          name: '3 6 6 1',
          tag: '#EUW',
          core: false,
        },
        {
          name: 'SignisAura',
          tag: 'CnAP',
          core: true,
        },
        {
          name: 'Alraune22',
          tag: 'CnAP',
          core: true,
        },
        {
          name: 'Aw3s0m3mag1c',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'Gnerfedurf',
          tag: 'BCH',
          core: true,
        },
        {
          name: 'Gnoblin',
          tag: 'BCH',
          core: true,
        },
        {
          name: 'VredVampire',
          tag: '2503',
          core: false,
        },
        {
          name: 'D3M0NK1LL3RG0D',
          tag: 'EUW',
          core: true,
        },
        {
          name: 'GLOMVE',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'hide on büschli',
          tag: 'EUW',
          core: true,
        },
        {
          name: 'IBlueSnow',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'Nayan Stocker',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'Norina Michel',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'pentaskill',
          tag: 'CnAP',
          core: true,
        },
        {
          name: 'Pollux',
          tag: '2910',
          core: true,
        },
        {
          name: 'Polylinux',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'Prequ',
          tag: 'EUW',
          core: true,
        },
        {
          name: 'Sausage Revolver',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'swiss egirI',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'TCT Tawan',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'The 26th Bam',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'Theera3rd',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'Zinsstro',
          tag: 'EUW',
          core: false,
        },
        {
          name: 'WhatThePlay',
          tag: 'CnAP',
          core: true,
        },
        {
          name: 'pentaskill',
          tag: 'CnAP',
          core: true,
        },
        {
          name: 'Árexo',
          tag: 'CNAP',
          core: true,
        },
      ];
    }
  }

  async fillSummoners() {
    const summonerObjects: SummonerDTO[] = [];
    for (const account of this.accountNames) {
      if (account.core) {
        const riotData = await this.riotHelper.getSummonerByAccountTag(
          account.name,
          account.tag,
        );
        if (riotData) {
          summonerObjects.push(riotData);
        }
      }
    }
    await this.dbHelper.updateSummoners(summonerObjects);
  }
}

const task = new FillSummonersTask();
void task.fillSummoners();
