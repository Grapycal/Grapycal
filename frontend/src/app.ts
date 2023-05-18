import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic} from 'objectsync-client'

import { Node } from './sobjects/node'
import { Editor } from './ui_utils/editor'
import { Root } from './sobjects/root'
import { expose } from './devUtils'
import { Port } from './sobjects/port'

export const editor = new Editor();

const client = new ObjectSyncClient('ws://192.168.245.187:8765');
client.register(Root);
client.register(Node);
client.register(Port);

expose('c',client)