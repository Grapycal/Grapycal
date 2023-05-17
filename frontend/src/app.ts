import {ObjectSyncClient, SObject, StringTopic, DictTopic, IntTopic, SetTopic, FloatTopic, GenericTopic} from 'objectsync-client'

import { Node } from './sobjects/node'
import { Editor } from './ui_utils/editor'
import { Root } from './sobjects/root'

export const editor = new Editor();

const client = new ObjectSyncClient('ws://localhost:8765');
client.register(Root);
client.register(Node);
